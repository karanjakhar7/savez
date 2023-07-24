// Get all the radio buttons
const radioButtons = document.querySelectorAll('input[type="radio"]');
// Get the text input field
const textInput = document.getElementById('newCategory');

// Add an event listener to the text input
textInput.addEventListener('input', () => {
  // When text is typed in the text field, uncheck all the radio buttons
  radioButtons.forEach(radioButton => {
    radioButton.checked = false;
  });
});

function deletePost(postId) {
    fetch("/delete-post", {
      method: "POST",
      body: JSON.stringify({ postId: postId }),
    }).then((_res) => {
      window.location.href = "/saved";
    });
  }
  

// const category_form = document.getElementById("categoryForm");
// const customSubmitButton = document.getElementById("categorySubmit");

// // Add event listener to the custom submit button
// customSubmitButton.addEventListener("click", () => {
//     category_form.submit(); // Submit the form
// });