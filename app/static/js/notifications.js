// Храним ID уже отображенных уведомлений
const displayedNotifications = new Set()

async function loadNotifications() {
    console.log("loadNotifications")
    const res = await fetch("/api/notifications/inapp", {
        credentials: "include",
    })
    const data = await res.json()

    data.forEach(n => {
        if (!displayedNotifications.has(n.id)) {
            renderNotification(n)
            displayedNotifications.add(n.id)
        }
    })
}

function renderNotification(n) {
    const el = document.createElement("div")
    el.className = "notification"
    el.dataset.id = n.id

    el.innerHTML = `
        <div>
            <strong>${n.title}</strong>
            <p>${n.message}</p>
        </div>
        <button onclick="markRead('${n.id}', this)">✓</button>
    `
    document.getElementById("notifications-list").appendChild(el)
}

async function markRead(id, btn) {
    await fetch(`/api/notifications/${id}/read`, {method: "POST"})
    btn.parentElement.remove()
    displayedNotifications.delete(id)
}

function showToast(n) {
    const toast = document.createElement("div")
    toast.className = "toast"
    toast.innerHTML = `<strong>${n.title}</strong><p>${n.message}</p>`
    toast.onclick = () => {
        markRead(n.id, toast)
    }

    document.getElementById("toast-container").appendChild(toast)

    setTimeout(() => toast.remove(), 5000)
}

function prependNotification(n) {
    // Проверяем что уведомление еще не отображено
    if (!displayedNotifications.has(n.id)) {
        renderNotification(n)
        displayedNotifications.add(n.id)
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadNotifications()
    connectSSE()
})