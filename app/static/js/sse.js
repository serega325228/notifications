function connectSSE() {
    const source = new EventSource("/api/notifications/stream", {
        withCredentials: true,
    })

    source.onmessage = (event) => {
        const data = JSON.parse(event.data)
        showToast(data)
        prependNotification(data)
    }

    source.onerror = (error) => {
        console.error("SSE connection error:", error)
        source.close()
        // Переподключение через 5 секунд
        setTimeout(connectSSE, 5000)
    }
}