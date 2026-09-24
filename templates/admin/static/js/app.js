(function () {
  "use strict";

  /* ── Loader ─────────────────────────────────────────────── */
  window.addEventListener("load", function () {
    var loader = document.getElementById("loader");
    if (!loader) return;
    setTimeout(function () {
      loader.classList.add("done");
      setTimeout(function () { loader.remove(); }, 500);
    }, 900);
  });

  /* ── Audio helpers ──────────────────────────────────────── */
  function playSfx(id) {
    try {
      var a = document.getElementById(id);
      if (a) { a.currentTime = 0; a.play().catch(function () {}); }
    } catch (e) {}
  }

  function showToast(msg) {
    var t = document.getElementById("toast");
    if (!t) return;
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(t._timer);
    t._timer = setTimeout(function () { t.classList.remove("show"); }, 2200);
  }

  /* ── Search & filter ────────────────────────────────────── */
  var currentCat = "all";
  var currentQuery = "";

  function filterCards() {
    var cards = document.querySelectorAll(".card[data-id]");
    var visible = 0;
    cards.forEach(function (card) {
      var cat = card.dataset.category || "";
      var title = (card.dataset.title || "").toLowerCase();
      var kw = (card.dataset.keywords || "").toLowerCase();
      var catOk = currentCat === "all" || cat === currentCat;
      var q = currentQuery.toLowerCase();
      var qOk = !q || title.indexOf(q) !== -1 || kw.indexOf(q) !== -1 || cat.indexOf(q) !== -1;
      if (catOk && qOk) {
        card.classList.remove("hidden");
        visible++;
      } else {
        card.classList.add("hidden");
      }
    });
    var empty = document.getElementById("emptyState");
    if (empty) empty.hidden = visible > 0;
  }

  var searchToggle = document.getElementById("searchToggle");
  var searchWrap = document.getElementById("searchWrap");
  var searchClose = document.getElementById("searchClose");
  var searchInput = document.getElementById("searchInput");

  if (searchToggle) {
    searchToggle.addEventListener("click", function () {
      playSfx("sfx-click");
      searchWrap.classList.add("open");
      setTimeout(function () { if (searchInput) searchInput.focus(); }, 280);
    });
  }
  if (searchClose) {
    searchClose.addEventListener("click", function () {
      searchWrap.classList.remove("open");
      currentQuery = "";
      if (searchInput) searchInput.value = "";
      filterCards();
    });
  }
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      currentQuery = searchInput.value.trim();
      filterCards();
    });
  }

  document.getElementById("catsBar")?.addEventListener("click", function (e) {
    var chip = e.target.closest(".cat-chip");
    if (!chip) return;
    playSfx("sfx-click");
    currentCat = chip.dataset.cat;
    document.querySelectorAll(".cat-chip").forEach(function (c) {
      c.classList.toggle("active", c.dataset.cat === currentCat);
    });
    filterCards();
  });

  document.getElementById("resetFilters")?.addEventListener("click", function () {
    currentCat = "all";
    currentQuery = "";
    if (searchInput) searchInput.value = "";
    searchWrap?.classList.remove("open");
    document.querySelectorAll(".cat-chip").forEach(function (c) {
      c.classList.toggle("active", c.dataset.cat === "all");
    });
    filterCards();
  });

  /* ── Copy / Like / Share ────────────────────────────────── */
  var pendingCopy = null;

  function doCopy(text, id, btn) {
    function after() {
      playSfx("sfx-copy");
      showToast("✓ تم نسخ البرومبت");
      if (btn) {
        var count = btn.querySelector(".count");
        if (count) count.textContent = (parseInt(count.textContent, 10) || 0) + 1;
      }
      var sc = document.getElementById("statCopies");
      if (sc) sc.textContent = (parseInt(sc.textContent, 10) || 0) + 1;
      fetch("/api/prompt/" + id + "/copy", { method: "POST" }).catch(function () {});
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(after).catch(function () { fallback(text, after); });
    } else {
      fallback(text, after);
    }
  }

  function fallback(text, cb) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.cssText = "position:fixed;left:-9999px";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); cb(); } catch (e) { showToast("تعذر النسخ"); }
    document.body.removeChild(ta);
  }

  /* Mandatory ad before copy */
  function maybeShowAdThenCopy(text, id, btn) {
    pendingCopy = { text: text, id: id, btn: btn };
    fetch("/api/mandatory-ad")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok && data.ad) showAdModal(data.ad);
        else { doCopy(text, id, btn); pendingCopy = null; }
      })
      .catch(function () {
        doCopy(text, id, btn);
        pendingCopy = null;
      });
  }

  function showAdModal(ad) {
    var modal = document.getElementById("adModal");
    if (!modal) { if (pendingCopy) doCopy(pendingCopy.text, pendingCopy.id, pendingCopy.btn); return; }
    document.getElementById("adTitle").textContent = ad.title;
    document.getElementById("adText").textContent = ad.text;
    var btn = document.getElementById("adBtn");
    btn.textContent = ad.button_text || "زيارة";
    btn.href = ad.button_link || "#";
    var media = document.getElementById("adMedia");
    media.innerHTML = ad.image_url
      ? '<img src="' + ad.image_url + '" alt="">'
      : "";
    var sec = ad.duration_seconds || 5;
    var skip = document.getElementById("adSkip");
    var secEl = document.getElementById("adSec");
    var fill = document.getElementById("adTimerFill");
    skip.disabled = true;
    secEl.textContent = sec;
    fill.style.transition = "none";
    fill.style.transform = "scaleX(1)";
    modal.hidden = false;
    modal.classList.add("open");
    document.body.style.overflow = "hidden";

    requestAnimationFrame(function () {
      fill.style.transition = "transform " + sec + "s linear";
      fill.style.transform = "scaleX(0)";
    });

    var left = sec;
    var timer = setInterval(function () {
      left--;
      secEl.textContent = Math.max(0, left);
      if (left <= 0) {
        clearInterval(timer);
        skip.disabled = false;
        skip.textContent = "تخطي";
      }
    }, 1000);

    skip.onclick = function () {
      if (skip.disabled) return;
      clearInterval(timer);
      modal.classList.remove("open");
      setTimeout(function () { modal.hidden = true; }, 280);
      document.body.style.overflow = "";
      if (pendingCopy) {
        doCopy(pendingCopy.text, pendingCopy.id, pendingCopy.btn);
        pendingCopy = null;
      }
    };
  }

  document.getElementById("masonryGrid")?.addEventListener("click", function (e) {
    var copyBtn = e.target.closest(".copy-btn");
    if (copyBtn) {
      e.stopPropagation();
      var id = copyBtn.dataset.id;
      var prompt = copyBtn.dataset.prompt;
      maybeShowAdThenCopy(prompt, id, copyBtn);
      return;
    }

    var likeBtn = e.target.closest(".like-btn");
    if (likeBtn) {
      e.stopPropagation();
      var id = likeBtn.dataset.id;
      playSfx("sfx-like");
      likeBtn.classList.add("liked");
      var icon = likeBtn.querySelector("i");
      if (icon) icon.className = "ph-light ph-heart-fill";
      var count = likeBtn.querySelector(".count");
      if (count) count.textContent = (parseInt(count.textContent, 10) || 0) + 1;
      showToast("❤️ شكراً");
      fetch("/api/prompt/" + id + "/like", { method: "POST" }).catch(function () {});
      return;
    }

    var shareBtn = e.target.closest(".share-btn");
    if (shareBtn) {
      e.stopPropagation();
      var id = shareBtn.dataset.id;
      var title = shareBtn.dataset.title || "برومبت";
      var text = "✦ " + title + "\n\n— من مكتبة خيال";
      fetch("/api/prompt/" + id + "/share", { method: "POST" }).catch(function () {});
      if (navigator.share) {
        navigator.share({ title: title, text: text }).catch(function () {});
      } else {
        doCopy(text, id, null);
        showToast("تم نسخ رابط المشاركة");
      }
      return;
    }

    var card = e.target.closest(".card");
    if (card) {
      playSfx("sfx-click");
      openModal(card);
    }
  });

  /* ── Modal ──────────────────────────────────────────────── */
  var selectedId = null;
  var selectedPrompt = "";

  function openModal(card) {
    var modal = document.getElementById("promptModal");
    if (!modal) return;
    selectedId = card.dataset.id;
    var copyBtn = card.querySelector(".copy-btn");
    selectedPrompt = copyBtn ? copyBtn.dataset.prompt : "";
    document.getElementById("modalCat").textContent = card.dataset.category || "";
    document.getElementById("modalTitle").textContent = card.dataset.title || card.querySelector(".card-title")?.textContent || "";
    var author = card.querySelector(".card-author");
    document.getElementById("modalAuthor").textContent = author ? author.textContent.trim() : "";
    document.getElementById("modalPrompt").textContent = selectedPrompt;
    modal.hidden = false;
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    var modal = document.getElementById("promptModal");
    if (!modal) return;
    modal.classList.remove("open");
    setTimeout(function () { modal.hidden = true; }, 280);
    document.body.style.overflow = "";
  }

  document.getElementById("modalClose")?.addEventListener("click", closeModal);
  document.getElementById("promptModal")?.addEventListener("click", function (e) {
    if (e.target.id === "promptModal") closeModal();
  });
  document.getElementById("modalCopy")?.addEventListener("click", function () {
    if (selectedPrompt && selectedId) maybeShowAdThenCopy(selectedPrompt, selectedId, null);
  });
  document.getElementById("modalShare")?.addEventListener("click", function () {
    var title = document.getElementById("modalTitle")?.textContent || "برومبت";
    var text = "✦ " + title + "\n\n" + selectedPrompt + "\n\n— من مكتبة خيال";
    if (navigator.share) {
      navigator.share({ title: title, text: text }).catch(function () {});
    } else {
      doCopy(text, selectedId, null);
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });
})();
