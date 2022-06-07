import { initializeApp } from "firebase/app";
import { getFirestore } from '@firebase/firestore';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyDRohxCTrU4f4qk9e3rsbA-jh3Cv6PCZi0",
  authDomain: "se-sanbedalaw.firebaseapp.com",
  projectId: "se-sanbedalaw",
  storageBucket: "se-sanbedalaw.appspot.com",
  messagingSenderId: "884352751776",
  appId: "1:884352751776:web:c4a51f84ebcb5a300e51c5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const db = getFirestore(app);
export const auth = getAuth(app);