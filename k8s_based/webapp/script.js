// First, we register the service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('firebase-messaging-sw.js')
    .then(function(registration) {
      console.log('Service Worker registered with scope:', registration.scope);
      // ONLY initialize Firebase after the service worker is active
      return navigator.serviceWorker.ready;
    })
    .then(function() {
      console.log("Service worker is active now");
      // Now initialize Firebase
      initializeFirebase();
    })
    .catch(function(err) {
      console.error('Service Worker registration failed:', err);
    });
} else {
  console.error('Service workers are not supported in this browser');
}

// Move ALL Firebase related code into this function
function initializeFirebase() {
  const firebaseConfig = {
    apiKey: "AIzaSyChrr38ouUgO8APXZ8f9wOB23W0IsxKQTY",
    authDomain: "notify-29be5.firebaseapp.com",
    projectId: "notify-29be5",
    storageBucket: "notify-29be5.firebasestorage.app",
    messagingSenderId: "1013002547690",
    appId: "1:1013002547690:web:c8218c289b8552a6884293"
  };

  // Initialize Firebase inside this function
  firebase.initializeApp(firebaseConfig);
  const messaging = firebase.messaging();

  // Set up message handler
  messaging.onMessage((payload) => {
    console.log('[script.js] Message received in foreground:', payload);
    
    // Create notification manually for foreground messages
    if (payload.notification) {
      const { title, body } = payload.notification;
      new Notification(title, { body });
    }
  });
  
  // Now request permissions
  requestNotificationPermission(messaging);
}

async function requestNotificationPermission(messaging) {
  try {
    const permission = await Notification.requestPermission();
    if (permission === "granted") {
      console.log("Notification permission granted.");
      getFcmToken(messaging);
    } else {
      console.error("Unable to get permission to notify.");
    }
  } catch (err) {
    console.error("Error requesting permission:", err);
  }
}

async function getFcmToken(messaging) {
  try {
    // Get token
    const currentToken = await messaging.getToken();
    console.log("FCM Token:", currentToken);

    // Send to backend
    await fetch('http://34.131.193.34:5000/register-token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        token: currentToken,
        orderid: 1
      })
    });
    console.log("Token sent to backend");
  } catch (err) {
    console.error("Error retrieving or sending token:", err);
  }
}