console.log("Custom script loaded");
const style = document.createElement('style');
style.innerHTML = css;
gradioApp().head.append(style);  
  gradioApp().querySelectorAll(
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
  gradioApp().querySelectorAll(
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
