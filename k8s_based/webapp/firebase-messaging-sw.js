// Import the Firebase scripts needed for FCM
importScripts("https://www.gstatic.com/firebasejs/9.20.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.20.0/firebase-messaging-compat.js");

// Replace with your Firebase project configuration
const firebaseConfig = {
    apiKey: "AIzaSyChrr38ouUgO8APXZ8f9wOB23W0IsxKQTY",
    authDomain: "notify-29be5.firebaseapp.com",
    projectId: "notify-29be5",
    storageBucket: "notify-29be5.firebasestorage.app",
    messagingSenderId: "1013002547690",
    appId: "1:1013002547690:web:c8218c289b8552a6884293"
  };


firebase.initializeApp(firebaseConfig);


const messaging = firebase.messaging();


messaging.onBackgroundMessage((payload) => {
  console.log("[firebase-messaging-sw.js] Received background message:", payload);
  const { title, body } = payload.notification || {};
  self.registration.showNotification(title, { body });
});