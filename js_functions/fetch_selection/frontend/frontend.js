window.addEventListener("load", function () {
    const sendSelectedText = () => {
      const selectedText = window.getSelection().toString();
      Streamlit.setComponentValue(selectedText);
    };
  
    const button = document.getElementById("fetch-btn");
    if (button) {
      button.addEventListener("click", sendSelectedText);
    }
  });
  