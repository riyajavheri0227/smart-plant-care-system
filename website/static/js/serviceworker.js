self.addEventListener("install", function(event) {
    console.log("Service Worker Installed");
    self.skipWaiting();
});

self.addEventListener("activate", function(event) {
    console.log("Service Worker Activated");
    event.waitUntil(self.clients.claim());
});

self.addEventListener("push", function(event) {

    let data = {};

    if (event.data) {
        data = event.data.json();
    }

    event.waitUntil(
        self.registration.showNotification(
            data.title || "🌱 Smart Plant Care",
            {
                body: data.body || "You have a plant reminder.",
                icon: "/static/images/logo.jpeg",
                badge: "/static/images/logo.jpeg"
            }
        )
    );
});