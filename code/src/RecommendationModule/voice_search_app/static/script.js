function textSearch() {
  let query = document.getElementById("searchBox").value;
  fetch("/search/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: "query=" + encodeURIComponent(query),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Response received:", data);
      document.getElementById("result").innerHTML = marked.parse(data.response);
    })
    .catch((error) => console.error("Error in textSearch:", error));
}

function voiceSearch() {
  fetch("/voice/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      let searchBox = document.getElementById("searchBox");
      searchBox.value = data.response;
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
