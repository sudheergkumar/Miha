document.addEventListener("DOMContentLoaded", function () {
  const sendButton = document.getElementById("send-btn");
  const userInput = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  sendButton.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
      appendMessage("user-message", message);
      fetchResponse(message);
      userInput.value = "";
    }
  }

  function appendMessage(className, message) {
    const messageElement = document.createElement("div");
    messageElement.className = `message ${className}`;
    if (className === "bot-message") {
      messageElement.innerHTML = message; // Use innerHTML to render HTML content
    } else {
      messageElement.innerText = message;
    }
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function fetchResponse(message) {
    fetch("/get_response", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.response) {
          appendMessage("bot-message", data.response);
          if (data.map) {
            showMap(data.map);
          }
        } else {
          appendMessage("bot-message", "Sorry, something went wrong.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        appendMessage("bot-message", "Sorry, something went wrong.");
      });
  }
});
