<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>mainWindow</class>
 <widget class="QWidget" name="mainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>730</width>
    <height>527</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Echo</string>
  </property>
  <layout class="QHBoxLayout" name="horizontalLayout_3">
   <item>
    <widget class="QGroupBox" name="chatGroup">
     <property name="title">
      <string>Chat</string>
     </property>
     <layout class="QVBoxLayout" name="verticalLayout_2">
      <item>
       <widget class="QListWidget" name="chatArea"/>
      </item>
      <item>
       <widget class="QGroupBox" name="messageGroup">
        <property name="title">
         <string>Message</string>
        </property>
        <layout class="QHBoxLayout" name="horizontalLayout">
         <item alignment="Qt::AlignBottom">
          <widget class="QTextEdit" name="messageInput"/>
         </item>
         <item>
          <widget class="QPushButton" name="sendButton">
           <property name="text">
            <string>Send</string>
           </property>
          </widget>
         </item>
        </layout>
       </widget>
      </item>
     </layout>
    </widget>
   </item>
   <item>
    <widget class="QGroupBox" name="contactsGroup">
     <property name="maximumSize">
      <size>
       <width>345</width>
       <height>16777215</height>
      </size>
     </property>
     <property name="title">
      <string>Contact list</string>
     </property>
     <layout class="QVBoxLayout" name="verticalLayout_3">
      <item alignment="Qt::AlignRight">
       <widget class="QPushButton" name="deleteContactButton">
        <property name="text">
         <string>X</string>
        </property>
       </widget>
      </item>
      <item>
       <widget class="QListWidget" name="contactList"/>
      </item>
      <item>
       <widget class="QGroupBox" name="newContactGroup">
        <property name="title">
         <string>New contact</string>
        </property>
        <layout class="QHBoxLayout" name="horizontalLayout_4">
         <item>
          <widget class="QLineEdit" name="newContactInput"/>
         </item>
         <item>
          <widget class="QPushButton" name="newContactButton">
           <property name="text">
            <string>Add</string>
           </property>
          </widget>
         </item>
        </layout>
       </widget>
      </item>
     </layout>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
