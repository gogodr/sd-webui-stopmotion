console.log("Custom script loaded");
const style = document.createElement('style');
style.innerHTML = css;
document
  .querySelector("gradio-app")
  .shadowRoot.append(style);
  
document
  .querySelector("gradio-app")
  .shadowRoot.querySelectorAll(
    "#smcn-tabs_container .tabs > div:first-child button"
  )
  .forEach((btn, i) => {
    if (i >= 1) {
      btn.style.display = "none";
    } else {
      btn.style.display = "block";
    }
  });

window.smcn_updateTabs = (index) => {
  document
    .querySelector("gradio-app")
    .shadowRoot.querySelectorAll(
      "#smcn-tabs_container .tabs > div:first-child button"
    )
    .forEach((btn, i) => {
      if (i >= index) {
        btn.style.display = "none";
      } else {
        btn.style.display = "block";
      }
    });
  return [];
};

return [];
