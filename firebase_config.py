import pyrebase

config = {
    'apiKey': "AIzaSyDRohxCTrU4f4qk9e3rsbA-jh3Cv6PCZi0",
    'authDomain': "se-sanbedalaw.firebaseapp.com",
    'projectId': "se-sanbedalaw",
    'storageBucket': "se-sanbedalaw.appspot.com",
    'messagingSenderId': "884352751776",
    'appId': "1:884352751776:web:c4a51f84ebcb5a300e51c5",
    'databaseURL' : "https://se-sanbedalaw-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()