// static/js/notifications.js

document.addEventListener('DOMContentLoaded', function() {
    const notificationBadge = document.getElementById('notification-badge');

    function updateBadgeCount(count) {
        if (count > 0) {
            notificationBadge.innerText = count;
            notificationBadge.style.display = 'inline';
        } else {
            notificationBadge.style.display = 'none';
        }
    }

    // Initial check for unread notifications
    fetch('/notifications/count/')
        .then(response => response.json())
        .then(data => {
            updateBadgeCount(data.count);
        });

    // WebSocket connection (auto-detect ws/wss)
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    console.log('WebSocket URL:', wsScheme + '://' + window.location.host + '/ws/notifications/');
    const socket = new WebSocket(wsScheme + '://' + window.location.host + '/ws/notifications/');

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log('Received real-time notification:', data);

        // Update the badge count
        const currentCount = parseInt(notificationBadge.innerText) || 0;
        updateBadgeCount(currentCount + 1);

        // Optional: Show a popup or notification toast
        alert(data.message);
    };

    socket.onclose = function(e) {
        console.log('WebSocket closed unexpectedly');
    };
});