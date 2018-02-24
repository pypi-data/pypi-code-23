from bitcoin import *
import hashlib, ecdsa, binascii
from blockchain import blockexplorer
from ecdsa import SigningKey, SECP256k1
from operator import itemgetter
import os
try:
    import httplib
except:
    import http.client as httplib


def CheckConnection():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

def sign_tx(private_key, hex_data):
	public_address = pubtoaddr(privtopub(private_key))
	pubkey = privtopub(private_key)
	split_data = hex_data.split("00ffffffff")
	input_stubs = split_data[:-1]
	output_stub = split_data[-1]
	pre_sig_script = '1976a914'+b58check_to_hex(public_address)+'88acffffffff'
	sig_stubs = []
	for i in range(len(input_stubs)):
		signing_message = ''
		for j in range(i):
			signing_message += input_stubs[j]+'00ffffffff'
		signing_message += input_stubs[i] + pre_sig_script
		for k in range(i+1, len(input_stubs)):
			signing_message += input_stubs[k]+'00ffffffff'
		signing_message += output_stub+'01000000'
		hashed_message = hashlib.sha256(hashlib.sha256(signing_message.decode('hex')).digest()).digest()
		signingkey = ecdsa.SigningKey.from_string(b58check_to_hex(private_key).decode('hex'), curve=ecdsa.SECP256k1)
		SIG = binascii.hexlify(signingkey.sign_digest(hashed_message, sigencode=ecdsa.util.sigencode_der_canonize))
		ScriptSig = hex(len(SIG+'01')/2)[2:] + SIG + '01' + hex(len(pubkey)/2)[2:] + pubkey	
		ScriptLength = hex(len(ScriptSig)/2)[2:]
		sig_stub = ScriptLength+ScriptSig+'ffffffff'
		sig_stubs.append(sig_stub)
	bytes_ = ''
	for q in range(len(sig_stubs)):
		bytes_ += input_stubs[q]+sig_stubs[q]
	bytes_ += output_stub
	return bytes_

def hu_readable():
	try:
		readable = decode_tx(sys.argv[1])
	except:
		readable = decode_tx(raw_input("input transaction hex:"))

	print "TRANSACTION SUMMARY"
	print "Size (in bytes):", readable['size']
	print "All involved parties:", readable['addresses']
	print
	for i in range (len(readable['inputs'])):
		print "Input %s:" %(i+1)
		print "    " + str(readable['inputs'][i]['value']) + " satoshis from " + readable['inputs'][i]['address']
		print

	for i in range (len(readable['outputs'])):
		print "Output %s:" %(i+1)
		print "    " + str(readable['outputs'][i]['value']) + " satoshis to " + readable['outputs'][i]['address']
		print

	print "Miner Fee: "+ str(readable['fees'])+ " or " + str(readable['fees']/float(readable['size']))+ " sat/byte"


def decode_tx(bytes_):
	readable = deserialize(bytes_)
	inputs_decoded = [{'address': blockexplorer.get_tx(i['outpoint']['hash']).outputs[i['outpoint']['index']].address, 'value' : blockexplorer.get_tx(i['outpoint']['hash']).outputs[i['outpoint']['index']].value, 'prev_hash':i['outpoint']['hash'], 'index':i['outpoint']['index'], 'script':i['script'], 'sequence':i['sequence']}for i in readable['ins']]
	outputs_decoded = [{'address' : hex_to_b58check(i['script'][6:-4]), 'value': i['value'], 'script':i['script']} for i in readable['outs']]
	all_addresses = list(set([i['address'] for i in inputs_decoded] + [j['address'] for j in outputs_decoded]))
	full_decode = {'addresses': all_addresses, 'version': readable['version'], 'size':len(bytes_)/2, 'fees': sum([i['value'] for i in inputs_decoded]) - sum([i['value'] for i in outputs_decoded]), 'locktime':readable['locktime'], 'inputs':inputs_decoded, 'outputs':outputs_decoded}
	return full_decode

def run():
	if CheckConnection() == False:
		print "You are OFFLINE."
		print
		print "Send BTC Simply: Secure Offline Signature from the Shell"
		print
		try:
			signed_data = sign_tx(raw_input("enter sender's private key:\n"),raw_input("\n\nenter unsigned transaction data for signing:\n"))
			os.system('reset')
			if signed_data != -1:
				print "Success! Transaction Signed."
				print
				print "Signed Transaction Data:"
				print signed_data
				print
				print "Copy the data above to broadcast this transaction." 
			else:
				print "Error Signing Transaction. Double check input fields are correct and try again.\nGoodbye."
		except:
			os.system('reset')
			print "Error Signing Transaction. Double check input fields and try again.\nGoodbye."

	else:
		print "You are ONLINE."
		print
		print "FOR YOUR OWN SECURITY:\nYour private key is unsafe if stored or input on any online device.\nScript will not run if you are potentially exposed to any connection.\nMake sure this device is completely disconnected and try again.\nGoodbye."