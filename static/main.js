document.addEventListener("DOMContentLoaded", () => {
  const generatePostButton = document.getElementById("generate_post_button");
  const postSubjectInput = document.getElementById("post_subject");
  const numberOfPostsInput = document.getElementById("number_of_posts");
  const generatedPostsContainer = document.getElementById("generated_posts");
  const schedulePostsButton = document.getElementById("schedule_posts_button");
  const startDateInput = document.getElementById("start_date");
  const startTimeInput = document.getElementById("start_time");
  const intervalInput = document.getElementById("interval_value");
  const intervalUnitInput = document.getElementById("interval_unit");

  async function generatePosts() {
    const formData = new FormData(postSubjectInput.form);
    formData.append("number_of_posts", numberOfPostsInput.value);
  
    const response = await fetch("/generate_post", {
      method: "POST",
      body: formData,
    });
  
    const data = await response.json();
    const generatedPosts = data.generated_posts;
    const postIds = data.post_ids; // New: Get post ids from the response
  
    generatedPostsContainer.innerHTML = "";
    generatedPosts.forEach((post, index) => {
      const postElement = document.createElement("div");
      const postId = postIds[index]; // New: Get the post id from the postIds array
      postElement.innerHTML = `
        <textarea name="post_${index}">${post}</textarea>
        <button class="approve_post_button" data-post-id="${postId}">Approve</button>
      `;
      generatedPostsContainer.appendChild(postElement);
    });

    const approvePostButtons = document.querySelectorAll(".approve_post_button");
    approvePostButtons.forEach((button) => {
      button.addEventListener("click", async (event) => {
        event.preventDefault();
        const postElement = event.target.previousElementSibling;
        const content = postElement.value;
        const post_id = event.target.dataset.postId;
        const formData = new FormData();
        formData.append("content", content);
        formData.append("post_id", post_id);

        const response = await fetch("/approve_post", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          event.target.setAttribute("disabled", "true");
          event.target.textContent = "Approved";
        } else {
          alert("Error approving the post.");
        }
      });
    });
  }

  async function schedulePosts() {
    const formData = new FormData();
    formData.append("start_date", startDateInput.value);
    formData.append("start_time", startTimeInput.value);
    formData.append("interval_value", intervalInput.value);
    formData.append("interval_unit", intervalUnitInput.value);

    const postElements = generatedPostsContainer.getElementsByTagName("textarea");
    for (const postElement of postElements) {
      formData.append("posts[]", postElement.value);
    }

    const response = await fetch("/schedule_posts", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      alert("Posts scheduled successfully.");
    } else {
      const errorText = await response.text();
      alert(`Error scheduling posts: ${errorText}`);
    }
  }

  generatePostButton.addEventListener("click", (event) => {
    event.preventDefault();
    generatePosts();
  });

  schedulePostsButton.addEventListener("click", (event) => {
    event.preventDefault();
    schedulePosts();
  });
});
