// 🎭 Chatbot Toggle Button
document.getElementById("chatbot_toggle").onclick = function () {
  let chatbot = document.getElementById("chatbot");
  let toggleIcons = document.getElementById("chatbot_toggle").children;

  chatbot.classList.toggle("collapsed");
  toggleIcons[0].style.display = chatbot.classList.contains("collapsed") ? "" : "none";
  toggleIcons[1].style.display = chatbot.classList.contains("collapsed") ? "none" : "";
};

document.getElementById("chatbot_toggle").onclick = function () {
  let chatbot = document.getElementById("chatbot");
  chatbot.classList.toggle("collapsed");

  if (!chatbot.classList.contains("collapsed")) {
    scrollToBottom();
  }
}

// 🌟 Chatbot Constants
const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

const BOT_IMG = "static/img/mhcicon.png";
const PERSON_IMG = "static/img/person.png";
const BOT_NAME = "Psychiatrist Bot";
const PERSON_NAME = "You";

// 🏷️ Floating Date Toast
const floatingDate = document.createElement("div");
floatingDate.className = "floating-date-toast";
floatingDate.style.display = "none";
document.body.appendChild(floatingDate);

// 📜 Load Chat History (if exists)
loadChatHistory();

// 📩 Handle User Input
msgerForm.addEventListener("submit", event => {
  event.preventDefault();
  const msgText = msgerInput.value.trim();
  if (!msgText) return;

  appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
  msgerInput.value = "";
  botResponse(msgText);
});

// 🔄 Append Message to Chat Window
function appendMessage(name, img, side, text, timestamp) {
  const chatWindow = document.querySelector(".msger-chat");

  let messageDate = timestamp ? new Date(timestamp) : new Date();
  let formattedDate = messageDate.toLocaleDateString("en-US", { month: 'long', day: 'numeric', year: 'numeric' });
  let formattedTime = messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // Check if a date divider is needed
  let lastDate = document.querySelector(".msger-chat").getAttribute("data-last-date");
  if (lastDate !== formattedDate) {
    chatWindow.insertAdjacentHTML("beforeend", `<div class="chat-date-divider">${formattedDate}</div>`);
    document.querySelector(".msger-chat").setAttribute("data-last-date", formattedDate);
  }

  const msgHTML = `
  <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img})"></div>
      <div class="msg-bubble">
          <div class="msg-info">
              <div class="msg-info-name">${name}</div>
              <div class="msg-info-time">${formatDate(new Date())}</div>
          </div>
          <div class="msg-text">${text}</div>
      </div>
  </div>`;

  chatWindow.insertAdjacentHTML("beforeend", msgHTML);
  scrollToBottom();
}

// 🤖 Handle Bot Response via AJAX
function botResponse(userMessage) {
  $.ajax({
    type: "POST",
    url: "/get_response",
    contentType: "application/json",
    data: JSON.stringify({ message: userMessage }),
    success: function (data) {
      const botMessage = data.response || "I'm sorry, I didn't understand that.";
      appendMessage(BOT_NAME, BOT_IMG, "left", botMessage);
    },
    error: function () {
      appendMessage(BOT_NAME, BOT_IMG, "left", "⚠️ Error connecting to chatbot.");
    }
  });
}

// 💾 Save Chat History to Session Storage
function saveChatHistory() {
  let chatHistory = msgerChat.innerHTML;
  sessionStorage.setItem("chat_history", chatHistory);
}

// 🔄 Load Chat History from Session Storage or Database
function loadChatHistory() {
  // Load chat history from sessionStorage first
  let storedHistory = sessionStorage.getItem("chat_history");
  if (storedHistory) {
    msgerChat.innerHTML = storedHistory;
  } else {
    // Fetch chat history from the database
    $.ajax({
      type: "GET",
      url: "/chat_history",
      success: function (data) {
        console.log(data);
        if (data.response.length === 0) {
          appendMessage(BOT_NAME, BOT_IMG, "left", "Welcome! How can I assist you today?");
        } else {
          data.response.forEach(chat => {
            appendMessage(PERSON_NAME, PERSON_IMG, "right", chat[0], chat[2]);
            appendMessage(BOT_NAME, BOT_IMG, "left", chat[1], chat[2]);
          });
        }
      }
    });
  }
}

msgerChat.addEventListener("scroll", function () {
  let firstVisibleMsg = document.elementFromPoint(msgerChat.clientWidth / 2, 100);
  if (firstVisibleMsg) {
    let dateText = firstVisibleMsg.closest(".chat-date-divider");
    if (dateText) {
      floatingDate.textContent = dateText.innerText;
      floatingDate.style.display = "block";
    } else {
      floatingDate.style.display = "none";
    }
  }
});

// 🔄 Auto-scroll to bottom
function scrollToBottom() {
  msgerChat.scrollTop = msgerChat.scrollHeight;
}

// 🔍 Utility Functions
function get(selector, root = document) {
  return root.querySelector(selector);
}

function formatDate(date) {
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
}
