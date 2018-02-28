#!/usr/bin/python
"""
Copyright 2018 Zymbit, Inc.

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the 
"Software"), to deal in the Software without restriction, including 
without limitation the rights to use, copy, modify, merge, publish, 
distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to 
the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
"""
This script creates a destination partition as a LUKS keyed dm-crypt volume
and ext4 filesystem. Next, the contents of a source partition are copied to the
destination and the source is optionally erased.
"""

import argparse
import os
import errno
import subprocess
import shutil
import sys
import tarfile
from progress.bar import ShadyBar
import threading
import time
import inotify
import inotify.adapters

########################################################################
# Utility functions
########################################################################

class led_flash:
   def __init__(self):
      self.evt = threading.Event()
      self._thread = threading.Thread(target=self.led_worker)
      self.gap_time_ms = 0
      self.pulse_time_ms = 0
      self.num_pulses = 0
      self.invert = False
      self._thread.start()

   def led_worker(self):
      import zymkey
      total_flash_time_ms = None
      while True:
         iadj = 0
         if self.invert:
            iadj = 1
         if self.num_pulses:
            np = (self.num_pulses * 2) + iadj
            zymkey.client.led_flash(self.pulse_time_ms, off_ms=self.pulse_time_ms, num_flashes=np)
            total_flash_time_ms = float((np * self.pulse_time_ms) + self.gap_time_ms) / 1000.0
         else:
            total_flash_time_ms = None
         self.evt.wait(total_flash_time_ms)
         self.evt.clear()
   
ledf = None
prev_pct = None

def flash_zk_led(gap_time_ms, pulse_time_ms, num_pulses, invert=False):
   global ledf
   if ledf is None:
      ledf = led_flash()
      time.sleep(0.1)
   ledf.gap_time_ms = gap_time_ms
   ledf.pulse_time_ms = pulse_time_ms
   ledf.num_pulses = num_pulses
   ledf.invert = invert
   ledf.evt.set()
   
def get_part_uuid(dev_path):
   cmd = "blkid " + dev_path
   res = subprocess.check_output(cmd.split(), stderr=subprocess.PIPE).split()
   for field in res:
      if "PARTUUID" in field:
         field = field.replace("\"", "")
         return field

def unpack_tar(tar_path, dst, bar=None):
   with tarfile.open(tar_path, "r") as tf:
      tmembers = tf.getmembers()
      total_size = 0
      for tm in tmembers:
         total_size += tm.size
      cur_size = 0
      rem = 100.0
      for tm in tmembers:
         tf.extract(tm, path=dst)
         cur_size += tm.size
         pct_done = round((rem * cur_size) / total_size, 1)
         if not bar is None:
            global prev_pct
            if pct_done != prev_pct:
               bar.goto(pct_done)
               prev_pct = pct_done
      if not bar is None:
         bar.finish()

def do_fdisk(cmds, dev):
   cmdstr = "\n".join(cmds)
   fd_proc = subprocess.Popen(["fdisk", dev], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   fd_out = fd_proc.communicate(input=cmdstr)[0]
   fd_proc.wait()
   return fd_out
   
def startup_zkifc():
   # Kill zkifc if it is running
   cmd = "killall zkifc"
   try:
      subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)
      time.sleep(10)
   except:
      pass
   # Clear out the /var/lib/zymbit directory
   shutil.rmtree(zkdir)
   # Recreate the /var/lib/zymbit directory
   os.mkdir(zkdir)
   # Start up zkifc
   cmd = "/usr/bin/zkifc -s " + zkdir
   zkifc_proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   # Wait for zkifc to bind to the zymkey
   i = inotify.adapters.InotifyTree(zkdir)
   for event in i.event_gen():
      if event is not None:
         (header, type_names, watch_path, filename) = event
         if filename == "state" and "IN_CLOSE_WRITE" in type_names:
            break
   
"""
This function configures config.txt and cmdline.txt in /boot to boot
Raspberry Pi from the new crypto volume.
"""
def update_initramfs(mapper_name, rfs_part, etc_base_dir="/etc"):
   # Insure that the boot partition is mounted
   try:
      # We might want the boot partition to be configurable, but most
      # use cases will use the boot partition on the SD card which is
      # /dev/mmcblk0p1
      cmd = "mount /dev/mmcblk0p1 /boot"
      subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)
   except:
      pass
   #####################################################################
   # Modify config.txt so that an initramfs is used during boot
   #####################################################################
   with open("/boot/config.txt") as bfd:
      lines = bfd.readlines()
      # Remove any stale "initramfs" lines
      lines = [line for line in lines if not line.startswith("initramfs")]
      # Put a new initramfs line at the end of the file. This line
      # instructs the GPU to put the file "initrd" after the kernel 
      # image in memory. The kernel expects to find the initramfs after
      # its own image.
      lines.append("initramfs initrd.img followkernel")
      with open("/boot/config.txt", "w") as bwfd:
         bwfd.writelines(lines)
   #####################################################################
   # Modify cmdline.txt to boot to the dm-crypt volume
   #####################################################################
   with open("/boot/cmdline.txt") as bfd:
      fields = bfd.readline().split()
      # Chop out everything having to do with the old root
      fields = [field for field in fields if not field.startswith("root=") and not field.startswith("rootfstype=") and not field.startswith("cryptdevice=")]
      line = " ".join(fields)
      line = line + " root=/dev/mapper/" + mapper_name + " cyptdevice=" + rfs_part + ":" + mapper_name
      with open("/boot/cmdline.txt", "w") as bwfd:
         bwfd.write(line)
   #####################################################################
   # Write the i2c drivers to the initramfs staging area
   #####################################################################
   with open(etc_base_dir + "/initramfs-tools/modules") as ifd:
      lines = ifd.readlines()
      # Get rid of stale entries
      lines = [line for line in lines if not line.startswith("i2c-dev") and not line.startswith("i2c-bcm2835") and not line.startswith("i2c-bcm2708")]
      lines.append("i2c-dev\n")
      lines.append("i2c-bcm2835\n")
      lines.append("i2c-bcm2708\n")
      with open(etc_base_dir + "/initramfs-tools/modules", "w") as iwfd:
         iwfd.writelines(lines)
   #####################################################################
   # Create the initramfs
   #####################################################################
   print "Building initramfs"
   cmd = "uname -r"
   kernel_ver = subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)
   kernel_ver = kernel_ver.rstrip("\n\r")
   try:
      os.remove("/boot/initrd.img-" + kernel_ver)
   except:
      pass
   cmd = "update-initramfs -v -c -k " + kernel_ver
   subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)
   os.rename("/boot/initrd.img-" + kernel_ver, "/boot/initrd.img")
   
"""
create_zk_crypt_vol - This function creates a LUKS dm-crypt volume and formats 
is as ext4. The passphrase is randomly generated by Zymkey and consequently 
locked by Zymkey.
arguments:
   dst_partition     The destination partition. This argument can specify a 
                     specific partition (e.g. /dev/sda1) or a device (e.g. 
                     /dev/sda). If a device is specified, then /dev/sda1 is
                     assumed.
   src_path          The path to a directory, tarfile or partition that
                     is to be copied to the destination. If src_path is
                     actually a partition, src_is_partition should be 
                     set to True. If src_path is set to None, the 
                     destination partition is created without copying
                     any data to it.
   src_is_partition  If src_path specifies a path to a partition, this argument
                     should be set to True.
   force_creation    If this argument is False, the destination volume will not
                     be created if a volume already exists on the destination
                     device. If True, the destination will be destroyed and a
                     new volume will be created.
   dst_size          If this argument is 0, the remaining size on the 
                     destination device will be used to create the new 
                     partition. If this argument is "match", then an attampt
                     will be made to match the source partition size if one
                     is specified.
   crypt_crypt_mapper_name The name for the dm-crypt mapper volume. Defaults to 
                     "cryptfs".
   erase_src         If True, the source partition is erased.
   zero_dst          If True, the destination volume is filled with zeros after
                     creation. This action has the effect of writing a random
                     sequence on the physical media and can help prevent
                     various attacks on the physical media at the expense of 
                     extra creation time.
   mnt_entry         If not "None", entries in fstab and crypttab are added
                     with the value in this argument.
   mnt_cfg_base_path If mnt_entry is not "None", this argument specifies the
                     location where fstab and crypttab are found.
"""
def create_zk_crypt_vol(dst_dev,
                        dst_part_num="",
                        src_path=None, 
                        src_is_partition=False, 
                        force_creation=False, 
                        dst_size=0, 
                        crypt_mapper_name="cryptfs", 
                        erase_src=False, 
                        zero_dst=False,
                        mnt_entry=None, 
                        mnt_cfg_base_path="/etc"):
   
   dst_part = dst_dev + dst_part_num

   # Specify the destination size: if a source partition has been specified and 
   # the destination size is supposed to match, then we should find the source partition size now.
   if src_path and src_is_partition and dst_size == "match":
      if dst_size == "match":
         if not src_is_partition:
            # Find out which device the partition is attached to
            cmd = "df " + src_path
            src_part = subprocess.check_output(cmd.split(), stderr=subprocess.PIPE).split("\n")[1]
            src_part = src_part.split()[0]
         else:
            src_part = src_path
         cmd = "sfdisk -lqs " + src_part
         try:
            dst_size = subprocess.check_output(cmd.split())
         except:
            pass
         if dst_size == "" or int(dst_size) == 0:
            print "Cannot determine src partition size"
            exit()
   else:
      dst_size_k = dst_size / 1024
   if dst_size_k != 0:
      dst_size = "+" + str(dst_size_k) + "K"
   else:
      dst_size = ""

   tmp_pval = dst_part_num.rstrip("1234567890")
   dst_part_num_val = dst_part_num.replace(tmp_pval, "")
   # Find out if the destination partition already exists.
   if dst_part_num == "" and os.path.exists(dst_part):
      print dst_part + " already exists."
      # Delete the old destination partition
      if force_creation:
         print "Deleting existing partition"
         fd_cmds = ["d", dst_part_num_val, "w"]
         do_fdisk(fd_cmds, dst_dev)
      else:
         print "Exiting."
         exit()

   # Unmount potentially stale mounts and dm-crypt mappings
   try:
      cmd = "umount /dev/mapper/" + crypt_crypt_mapper_name
      subprocess.call(cmd.split(), stderr = subprocess.PIPE)
   except:
      pass
   try:
      cmd = "umount " + dst_part
      subprocess.call(cmd.split(), stderr = subprocess.PIPE)
   except:
      pass
   if src_path and src_is_partition:
      try:
         cmd = "umount " + src_path
         subprocess.call(cmd.split(), stderr = subprocess.PIPE)
      except:
         pass
   try:
      cmd = "cryptsetup luksClose " + crypt_crypt_mapper_name
      subprocess.call(cmd.split(), stderr = subprocess.PIPE)
   except:
      pass

   # Create the new partition
   print "Creating new partition"
   fd_cmds = ["n", "", dst_part_num_val, "", dst_size, "w"]
   do_fdisk(fd_cmds, dst_dev)
   # TODO: if dst_part_num_val was "", we need to find the partition
   # number that fdisk just created for us
   subprocess.check_output("partprobe", subprocess.PIPE)

   # Create the LUKS key using Zymkey's random number generator
   print "Creating random passphrase"
   import zymkey
   key = zymkey.client.get_random(512)
   # Lock the key up in the specified location
   print "Locking passphrase"
   locked_key_fn = "/var/lib/zymbit/" + crypt_mapper_name + ".key"
   zymkey.client.lock(key, locked_key_fn)
   # Format the LUKS dm-crypt volume
   print "Formatting LUKS volume"
   cmd = "cryptsetup -q -v luksFormat " + dst_part + " -"
   p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   p.communicate(input=key)
   p.wait()
   # Open the dm-crypt volume
   print "Opening LUKS volume"
   cmd = "cryptsetup luksOpen " + dst_part + " " + crypt_mapper_name + " --key-file=-"
   p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   p.communicate(input=key)
   p.wait()
   # Create the ext4 file system on the dm-crypt volume
   print "Creating ext4 file system"
   cmd = "mkfs.ext4 /dev/mapper/" + crypt_mapper_name
   subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)

   # Mount the destination volume now
   dst_mnt = "/mnt/" + crypt_mapper_name
   if not os.path.exists(dst_mnt):
      os.makedirs(dst_mnt)
   cmd = "mount /dev/mapper/" + crypt_mapper_name + " " + dst_mnt
   subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)

   # If a source partition was specified, mount the partition now and 
   # designate the mount point as the source path
   src_part = None
   if src_path and src_is_partition:
      src_part = src_path
      src_path = "/mnt/src_vol"
      # Mount the source partition
      if not os.path.exists(src_path):
         os.makedirs(src_path)
      cmd = "mount " + src_part + " " + src_path
      subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)
   # If a source was specified, copy the source files to the 
   # destination now
   if src_path:
      if os.path.isfile(src_path):
         # Source path must be tarfile...extract now
         print "Unpacking root file system archive"
         bar = ShadyBar(max=100, width=50, suffix="%(percent).1f%% [%(elapsed)ds]")
         unpack_tar(src_path, dst_mnt, bar)
      else:
         # Copy with rsync
         print "Copying source files"
         cmd = "rsync -axHAX --info=progress2 " + src_path + "/ " + dst_mnt
         subprocess.call(cmd.split(), stderr=subprocess.PIPE)
         # If specified, erase the source volume
         if args.erase_src:
            print "Erasing source partition"
            shutil.rmtree(src_path)
         # Finally, if a source partition was specified, unmount it and remove
         # the temporary mount point
         if src_part:
            cmd = "umount " + src_part
            subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)
            os.rmdir(src_path)

   # Zero out the remaining space on the destination if so configured
   if zero_dst:
      print "Zeroing out destination"
      # Write as many zeros as we can
      cmd = "dd if=/dev/zero of=" + dst_mnt + "/bigzero " + "bs=1M conv=fsync"
      try:
         subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)
      except:
         pass
      # Flush the file systems
      subprocess.call("sync")
      # Remove the big zero file
      os.remove(dst_mnt + "/bigzero")
      
   # Add the mount entry to fstab and crypttab if specified
   if mnt_entry:
      # Determine the UUID of the destination device
      mapper_fn = "/dev/mapper/" + crypt_mapper_name
      fstab_path = mnt_cfg_base_path + "/fstab"
      crypttab_path = mnt_cfg_base_path + "/crypttab"

      # Add new volume to end of fstab
      # First, create fstab if it isn't already present
      open(fstab_path, "a").close()
      with open(fstab_path, "r") as rfd:
         lines = rfd.readlines()
         me_str = " " + mnt_entry + " "
         lines = [line for line in lines if not line.startswith(mapper_fn) and not me_str in line]
         lines.append(mapper_fn + " " + mnt_entry + "             ext4    defaults,noatime  0       1\n")
         with open(fstab_path, "w") as wfd:
            wfd.writelines(lines)
      # Add new entry to crypttab
      # First, create crypttab if it isn't already present
      open(crypttab_path, "a").close()
      with open(crypttab_path, "r") as rfd:
         lines = rfd.readlines()
         lines = [line for line in lines if not line.startswith(crypt_mapper_name)]
         lines.append(crypt_mapper_name + "\t" + dst_part + "\t" + locked_key_fn + "\tluks,keyscript=/lib/cryptsetup/scripts/zk_get_key\n")
         with open(crypttab_path, "w") as wfd:
            wfd.writelines(lines)

   # Sync up the file system
   subprocess.check_output("sync", stderr=subprocess.PIPE)
   # Cleanly unmount everything
   cmd = "umount " + dst_mnt
   subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)
   os.rmdir(dst_mnt)
   cmd = "cryptsetup luksClose " + crypt_mapper_name
   subprocess.check_output(cmd.split(), stderr=subprocess.PIPE)


if __name__ == "__main__":

   # If we were called from the command line, parse the arguments
   parser = argparse.ArgumentParser(description="Create a LUKS dm-crypt volume with ext4 file system that is keyed and locked up using Zymkey."
                                                "Optionally, copy a source partition to the destination.")
   parser.add_argument("-d", "--dst-partition", required=True,        help="Specify the destination partition.")
   parser.add_argument("-s", "--src-path",                            help="Specify a source path to copy to the destination. -s and -p can't "
                                                                           "be specified at the same time.")
   parser.add_argument("-p", "--src-partition",                       help="Specify a source partition to copy to the destination. -s and -p "
                                                                           "can't be specified at the same time.")
   parser.add_argument("-c", "--force-creation", action="store_true", help="Forces creation of destination partition even if it already "
                                                                           "exists.")
   parser.add_argument("-m", "--match-src-size", action="store_true", help="Forces the destination partition to be the same size as the "
                                                                           "source partition.")
   parser.add_argument("-i", "--dst_size",                            help="Creates the destination partition with specific size. This "
                                                                           "value can be specified in the form \{size\}K/M/G. Example: "
                                                                           "\"-i 10G\" will create a partition of 10 gigabytes.")
   parser.add_argument("-n", "--crypt-mapper-name",                   help="Specify a different crypto file system mapper name for the "
                                                                           "dm-crypt volume. Defaults to cryptfs.")
   parser.add_argument("-e", "--erase-src", action="store_true",      help="Erase source when after the copy from source to destination "
                                                                           "completes.")
   parser.add_argument("-a", "--add-mnt-entry",                       help="Add entries to <mnt-entry-base-path>/etc/fstab and "
                                                                           "<mnt-entry-base-path>/etc/crypttab for the new volume. Example: "
                                                                           "\"-a /mnt/customer_data\" will add an entry to the end of "
                                                                           "<mnt-entry-base-path>/etc/fstab.")
   parser.add_argument("-b", "--mnt-cfg-base-path",                   help="If \"-a\" (--add-mnt-entry) is specified, this argument specifies "
                                                                           "the base path where fstab and crypttab are to be found. Defaults "
                                                                           "to \"/etc\".")
   parser.add_argument("-z", "--zero-dst", action="store_true",       help="Fill the destination partition with zeros. This has the effect of "
                                                                           "writing a random sequence on remaining partition space whcih is "
                                                                           "considered a best practice.")
                                                                     
   args = parser.parse_args()

   if args.src_path and args.src_partition:
      print "ERROR: source path and source partition (-s and -p) specified at the same time. Only one may be specified."
      parser.print_help(sys.stderr)
      exit()
      
   # Determine the mapper name
   crypt_mapper_name = "cryptfs"
   if args.crypt_mapper_name:
      crypt_mapper_name = args.crypt_mapper_name
      
   src_path = args.src_path
   src_is_partition = False
   if args.src_partition:
      src_path = args.src_partition
      src_is_partition = True
      
   dst_size = args.dst_size
   if not dst_size and args.match_src_size:
      dst_size = "match"
   dst_sz_base = dst_size.rstrip("KMG")
   mult = 1
   if dst_size.endswith("K"):
      mult = 1024
   elif dst_size.endswith("M"):
      mult = 1024 * 1024
   elif dst_size.endswith("G"):
      mult = 1024 * 1024 * 1024
   if mult != 1:
      dst_size = int(dst_sz_base) * mult
   else:
      dst_size = int(dst_size)
      
   create_zk_crypt_vol(args.dst_partition, 
                       src_path, 
                       src_is_partition, 
                       args.force_creation, 
                       dst_size, 
                       crypt_mapper_name, 
                       args.erase_src, 
                       args.zero_dst, 
                       args.add_mnt_entry,
                       args.mnt_cfg_base_path)
   print "Done."
