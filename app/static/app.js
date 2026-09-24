(function () {
  "use strict";

  function toast(msg) {
    var el = document.createElement("div");
    el.className = "flash success";
    el.style.cssText = "position:fixed;bottom:90px;left:50%;transform:translateX(-50%);z-index:200;white-space:nowrap;";
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, 2000);
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    var ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
    return Promise.resolve();
  }

  document.addEventListener("click", function (e) {
    var copyBtn = e.target.closest(".copy-btn");
    if (copyBtn) {
      var id = copyBtn.dataset.id;
      var body = copyBtn.dataset.body || "";
      copyText(body).then(function () {
        toast("✓ تم نسخ البرومبت");
        var c = copyBtn.querySelector(".count");
        if (c) c.textContent = (parseInt(c.textContent, 10) || 0) + 1;
      });
      fetch("/posts/" + id + "/copy", { method: "POST" }).catch(function () {});
      return;
    }

    var likeBtn = e.target.closest(".like-btn");
    if (likeBtn) {
      var id = likeBtn.dataset.id;
      fetch("/posts/" + id + "/like", { method: "POST", credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (!data.ok) return;
          likeBtn.classList.toggle("on", data.liked);
          var icon = likeBtn.querySelector("i");
          if (icon) icon.className = data.liked ? "ph-light ph-heart-fill" : "ph-light ph-heart";
          var c = likeBtn.querySelector(".count");
          if (c) c.textContent = data.like_count;
        })
        .catch(function () {});
      return;
    }

    var saveBtn = e.target.closest(".save-btn");
    if (saveBtn) {
      var id = saveBtn.dataset.id;
      fetch("/posts/" + id + "/save", { method: "POST", credentials: "same-origin" })
        .then(function (r) {
          if (r.status === 401) { location.href = "/auth/login"; return null; }
          return r.json();
        })
        .then(function (data) {
          if (!data || !data.ok) return;
          saveBtn.classList.toggle("on", data.saved);
          toast(data.saved ? "تم الحفظ" : "أُزيل من المحفوظات");
        })
        .catch(function () {});
    }
  });
})();