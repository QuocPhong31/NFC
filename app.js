fetch("http://127.0.0.1:5000/api/track-view", {
    method: "POST",
    credentials: "include"
  });
const API_BASE = "http://127.0.0.1:5000/";

// fetch("https://thanhtamtraquanp.pythonanywhere.com/api/track-view", {
//     method: "POST",
//     credentials: "include"
//   });
// const API_BASE = "https://thanhtamtraquanp.pythonanywhere.com/";



// ============================================================
// NFC PROFILE ROUTER
// ============================================================

function getNFCSlug() {

    const hash = window.location.hash;

    // Ví dụ:
    // #/p/tran-quoc-phong-1c583a

    if (!hash.startsWith("#/p/")) {
        return null;
    }

    const slug = hash.substring(4).trim();

    return slug || null;
}


// ============================================================
// LOAD PROFILE
// ============================================================

async function loadNFCProfile() {

    const slug = getNFCSlug();

    if (!slug) {
        return;
    }

    console.log("NFC profile slug:", slug);

    try {

        const response = await fetch(
            `${API_BASE}api/public/cards/${encodeURIComponent(slug)}`
        );

        if (!response.ok) {

            console.error(
                "API NFC trả về:",
                response.status
            );

            throw new Error(
                "Không tìm thấy profile NFC"
            );
        }

        const card = await response.json();

        console.log("NFC CARD:", card);

        renderNFCProfile(card);

    } catch (error) {

        console.error(
            "Không thể tải NFC profile:",
            error
        );

        document.body.innerHTML = `
            <div class="nfc-error-page">

                <div class="nfc-error-box">

                    <h1>
                        Không tìm thấy profile
                    </h1>

                    <p>
                        Không thể tải thông tin thẻ NFC.
                    </p>

                </div>

            </div>
        `;
    }
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

    return String(value ?? "")
        .replace(/[&<>"']/g, function (char) {

            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            }[char];

        });
}


// ============================================================
// ESCAPE ATTRIBUTE
// ============================================================

function escapeAttr(value) {

    return escapeHtml(value);
}


// ============================================================
// PLATFORM ICON
// ============================================================

function getPlatformIcon(platform) {

    const icons = {

        email:
            "https://api.iconify.design/mdi/email-outline.svg?color=%23ffffff",

        phone:
            "https://api.iconify.design/mdi/phone.svg?color=%23ffffff",

        mobile:
            "https://api.iconify.design/mdi/phone.svg?color=%23ffffff",

        facebook:
            "https://cdn.simpleicons.org/facebook/ffffff",

        instagram:
            "https://cdn.simpleicons.org/instagram/ffffff",

        threads:
            "https://cdn.simpleicons.org/threads/ffffff",

        x:
            "https://cdn.simpleicons.org/x/ffffff",

        twitter:
            "https://cdn.simpleicons.org/x/ffffff",

        youtube:
            "https://cdn.simpleicons.org/youtube/ffffff",

        tiktok:
            "https://cdn.simpleicons.org/tiktok/ffffff",

        linkedin:
            "https://cdn.simpleicons.org/linkedin/ffffff",

        whatsapp:
            "https://cdn.simpleicons.org/whatsapp/ffffff",

        telegram:
            "https://cdn.simpleicons.org/telegram/ffffff",

        discord:
            "https://cdn.simpleicons.org/discord/ffffff",

        skype:
            "https://cdn.simpleicons.org/skype/ffffff",

        zalo:
            "https://api.iconify.design/simple-icons/zalo.svg?color=%23ffffff",

        website:
            "https://api.iconify.design/mdi/web.svg?color=%23ffffff",

        company_url:
            "https://api.iconify.design/mdi/web.svg?color=%23ffffff",

        link:
            "https://api.iconify.design/mdi/link-variant.svg?color=%23ffffff",

        address:
            "https://api.iconify.design/mdi/map-marker.svg?color=%23ffffff",

        tax:
            "https://api.iconify.design/mdi/file-document-outline.svg?color=%23ffffff"

    };

    const icon =
        icons[String(platform || "").toLowerCase()];

    if (icon) {

        return `
            <img
                src="${icon}"
                alt=""
                class="nfc-item-icon-image"
            >
        `;

    }

    return "●";
}


// ============================================================
// NORMALIZE URL
// ============================================================

function normalizeUrl(value) {

    if (!value) {
        return "";
    }

    const text = String(value).trim();

    if (
        text.startsWith("http://") ||
        text.startsWith("https://")
    ) {
        return text;
    }

    return "https://" + text;
}


// ============================================================
// GET ITEM HREF
// ============================================================

function getItemHref(item) {

    const platform =
        String(item.platform || "").toLowerCase();

    const value =
        String(item.value || "").trim();

    if (!value) {
        return "#";
    }

    // EMAIL
    if (
        platform === "email" ||
        item.item_type === "email"
    ) {
        return `mailto:${value}`;
    }

    // PHONE
    if (
        platform === "phone" ||
        platform === "mobile" ||
        item.item_type === "phone"
    ) {

        const phone =
            value.replace(/[^\d+]/g, "");

        return `tel:${phone}`;
    }

    // URL
    return normalizeUrl(value);
}


// ============================================================
// SHOULD OPEN NEW TAB
// ============================================================

function isExternalItem(item) {

    const platform =
        String(item.platform || "").toLowerCase();

    return ![
        "email",
        "phone",
        "mobile"
    ].includes(platform);
}


// ============================================================
// RENDER ONE ITEM
// ============================================================

function renderNFCItem(item) {

    const platform =
        String(item.platform || "").toLowerCase();

    const category =
        String(item.category || "").toUpperCase();

    const title =
        item.display_title ||
        item.item_type ||
        item.platform ||
        "Thông tin";

    const value =
        item.value || "";

    if (!value) {
        return "";
    }

    // ========================================================
    // LINK
    // ========================================================

    const href =
        getItemHref(item);

    const external =
        isExternalItem(item);

    const icon =
        getPlatformIcon(platform);

    const isUrl =
        href.startsWith("http://") ||
        href.startsWith("https://");


    // ========================================================
    // HIỂN THỊ VALUE
    // ========================================================
    //
    // GENERAL:
    //   Email       → hiện email
    //   Phone       → hiện số
    //   Website     → hiện website
    //   Address     → hiện địa chỉ
    //
    // SOCIAL:
    //   Facebook    → không hiện URL
    //   Instagram   → không hiện URL
    //   TikTok      → không hiện URL
    //
    // MESSAGING:
    //   Zalo        → không hiện số
    //   WhatsApp    → không hiện số
    //   Telegram    → không hiện username/link
    //
    // ========================================================

    const showValue =
        category === "GENERAL" ||
        category === "";

    const strongTitle =
        category === "SOCIAL" ||
        category === "MESSAGING";


    return `

        <a
            class="nfc-item"
            href="${escapeAttr(href)}"

            ${
                external
                ?
                `
                target="_blank"
                rel="noopener noreferrer"
                `
                :
                ""
            }

        >

            <div class="nfc-item-icon">

                ${icon}

            </div>


            <div class="nfc-item-content">

                <div class="nfc-item-title ${strongTitle ? "nfc-item-title-strong" : ""}">

                    ${escapeHtml(title)}

                </div>


                ${
                    showValue
                    ?
                    `
                    <div class="nfc-item-value">

                        ${escapeHtml(value)}

                    </div>
                    `
                    :
                    ""
                }

            </div>


            ${
                isUrl
                ?
                `
                <div class="nfc-item-arrow">
                    ›
                </div>
                `
                :
                ""
            }

        </a>

    `;
}

// ============================================================
// RENDER CARD ITEMS
// ============================================================

function renderCardItems(card) {

    const items =
        Array.isArray(card.links)
            ? card.links
            : [];


    return items

        .filter(item => {

            const value =
                String(item.value || "")
                    .trim();

            return (
                value !== "" &&
                item.is_active !== false
            );

        })

        .map(item =>
            renderNFCItem(item)
        )

        .join("");
}

// ============================================================
// PUBLIC URL
// ============================================================

function getPublicProfileUrl(card) {

    const slug =
        card.slug ||
        getNFCSlug();

    return (
        window.location.origin +
        window.location.pathname +
        "#/p/" +
        encodeURIComponent(slug)
    );
}


// ============================================================
// SHARE MODAL
// ============================================================

function openShareModal(card) {

    const publicUrl =
        getPublicProfileUrl(card);

    const qrUrl =
        card.qrUrl || "";

    // Xóa modal cũ nếu tồn tại
    const old =
        document.getElementById("nfcShareModal");

    if (old) {
        old.remove();
    }


    // ========================================================
    // CREATE MODAL
    // ========================================================

    const modal =
        document.createElement("div");

    modal.id =
        "nfcShareModal";

    modal.className =
        "nfc-share-overlay";


    // ========================================================
    // MODAL HTML
    // ========================================================

    modal.innerHTML = `

        <div
            class="nfc-share-modal"
            onclick="event.stopPropagation()"
        >

            <!-- ==========================================
                 HEADER
            =========================================== -->

            <div class="nfc-share-header">

                <h2>
                    Chia sẻ
                </h2>

                <button
                    class="nfc-share-close"
                    onclick="closeShareModal()"
                    aria-label="Đóng"
                >

                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <path d="M6 18L18 6"></path>
                        <path d="M6 6L18 18"></path>
                    </svg>

                </button>

            </div>


            <!-- ==========================================
                 LINK + COPY
            =========================================== -->

            <div class="nfc-share-link-box">

                <div class="nfc-share-link-left">

                    <!-- LINK ICON -->

                    <svg
                        class="nfc-share-link-icon-svg"
                        width="22"
                        height="22"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <path
                            d="M10 13a5 5 0 0 0 7.07.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"
                        ></path>

                        <path
                            d="M14 11a5 5 0 0 0-7.07-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"
                        ></path>
                    </svg>


                    <!-- URL -->

                    <span class="nfc-share-link-text">

                        ${escapeHtml(publicUrl)}

                    </span>

                </div>


                <!-- COPY BUTTON -->

                <button
                    class="nfc-copy-button"
                    onclick="copyNFCLink('${escapeAttr(publicUrl)}')"
                    aria-label="Sao chép liên kết"
                >

                    <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >

                        <rect
                            x="9"
                            y="9"
                            width="13"
                            height="13"
                            rx="2"
                            ry="2"
                        ></rect>

                        <path
                            d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                        ></path>

                    </svg>

                </button>

            </div>


            <!-- ==========================================
                 QR CODE
            =========================================== -->

            <div class="nfc-qr-area">

                <div class="nfc-qr-card">


                    <!-- LEFT: QR + TEXT -->

                    <div class="nfc-qr-left">


                        <!-- QR -->

                        <div class="nfc-qr-container">

                            ${
                                qrUrl
                                ?
                                `
                                <img
                                    src="${escapeAttr(qrUrl)}"
                                    class="nfc-qr-image"
                                    alt="QR Code"
                                >
                                `
                                :
                                `
                                <div class="nfc-qr-missing">
                                    QR
                                </div>
                                `
                            }

                        </div>


                        <!-- TEXT -->

                        <div class="nfc-qr-info">

                            <div class="nfc-qr-title">

                                Thẻ profile

                            </div>

                            <div class="nfc-qr-subtitle">

                                QR Code

                            </div>

                        </div>

                    </div>


                    <!-- DOWNLOAD -->

                    ${
                        qrUrl
                        ?
                        `
                        <button
                            class="nfc-qr-download"
                            onclick="downloadNFCQR('${escapeAttr(qrUrl)}')"
                            aria-label="Tải QR Code"
                        >

                            <svg
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            >

                                <path
                                    d="M12 3v12"
                                ></path>

                                <path
                                    d="M7 10l5 5 5-5"
                                ></path>

                                <path
                                    d="M5 21h14"
                                ></path>

                            </svg>

                        </button>
                        `
                        :
                        ""
                    }

                </div>

            </div>


            <!-- ==========================================
                 SHARE BUTTON
            =========================================== -->

            <div class="nfc-native-share-area">

                <button
                    class="nfc-native-share"
                    onclick="nativeShareNFC('${escapeAttr(publicUrl)}')"
                    aria-label="Chia sẻ"
                >

                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >

                        <path
                            d="M12 16V4"
                        ></path>

                        <path
                            d="M8 8l4-4 4 4"
                        ></path>

                        <path
                            d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"
                        ></path>

                    </svg>

                </button>

            </div>


        </div>

    `;


    // ========================================================
    // CLICK OUTSIDE
    // ========================================================

    modal.addEventListener(
        "click",
        closeShareModal
    );


    document.body.appendChild(modal);


    document.body.classList.add(
        "nfc-modal-open"
    );
}

// ============================================================
// CLOSE SHARE MODAL
// ============================================================

function closeShareModal() {

    const modal =
        document.getElementById(
            "nfcShareModal"
        );

    if (modal) {
        modal.remove();
    }

    document.body.classList.remove(
        "nfc-modal-open"
    );
}


// ============================================================
// COPY LINK
// ============================================================

async function copyNFCLink(url) {

    try {

        await navigator.clipboard.writeText(url);

        alert("Đã sao chép link profile!");

    } catch (error) {

        console.error(
            "COPY ERROR:",
            error
        );

        const input =
            document.createElement("input");

        input.value = url;

        document.body.appendChild(input);

        input.select();

        document.execCommand("copy");

        input.remove();

        alert("Đã sao chép link profile!");
    }
}

// ============================================================
// DOWNLOAD QR CODE
// ============================================================

async function downloadNFCQR(url) {

    try {

        const response =
            await fetch(url);

        if (!response.ok) {
            throw new Error("Không thể tải QR");
        }

        const blob =
            await response.blob();

        const blobUrl =
            URL.createObjectURL(blob);

        const link =
            document.createElement("a");

        link.href =
            blobUrl;

        link.download =
            "nfc-profile-qr.png";

        document.body.appendChild(link);

        link.click();

        link.remove();

        setTimeout(
            () => URL.revokeObjectURL(blobUrl),
            1000
        );

    } catch (error) {

        console.error(
            "DOWNLOAD QR ERROR:",
            error
        );

        // fallback nếu Cloudinary không cho fetch
        window.open(
            url,
            "_blank"
        );

    }
}

// ============================================================
// NATIVE SHARE
// ============================================================

async function nativeShareNFC(url) {

    if (!navigator.share) {

        await copyNFCLink(url);

        return;
    }

    try {

        await navigator.share({

            title: "Danh thiếp NFC",

            text: "Xem danh thiếp của tôi",

            url: url

        });

    } catch (error) {

        console.log(
            "Share cancelled:",
            error
        );
    }
}


// ============================================================
// CREATE VCARD
// ============================================================

function createVCard(card) {

    const items =
        Array.isArray(card.links)
            ? card.links
            : [];


    let phone = "";
    let email = "";
    let website = "";
    let address = "";


    items.forEach(item => {

        const platform =
            String(
                item.platform || ""
            ).toLowerCase();

        const type =
            String(
                item.item_type || ""
            ).toLowerCase();

        const value =
            String(
                item.value || ""
            ).trim();


        if (!value) {
            return;
        }


        if (
            platform === "phone" ||
            platform === "mobile" ||
            type === "phone"
        ) {

            if (!phone) {
                phone = value;
            }

        }


        else if (
            platform === "email" ||
            type === "email"
        ) {

            if (!email) {
                email = value;
            }

        }


        else if (
            platform === "website" ||
            platform === "company_url" ||
            platform === "link" ||
            type === "website"
        ) {

            if (!website) {
                website = value;
            }

        }


        else if (
            platform === "address"
        ) {

            if (!address) {
                address = value;
            }

        }

    });


    const fullName =
        card.hoTen ||
        card.tenThe ||
        "NFC Contact";


    const company =
        card.congTy ||
        "";


    const title =
        card.chucVu ||
        "";


    const lines = [

        "BEGIN:VCARD",

        "VERSION:3.0",

        `FN:${escapeVCard(fullName)}`,

        `N:${escapeVCard(fullName)};;;;`,

        phone
            ? `TEL;TYPE=CELL:${escapeVCard(phone)}`
            : "",

        email
            ? `EMAIL;TYPE=INTERNET:${escapeVCard(email)}`
            : "",

        company
            ? `ORG:${escapeVCard(company)}`
            : "",

        title
            ? `TITLE:${escapeVCard(title)}`
            : "",

        website
            ? `URL:${escapeVCard(normalizeUrl(website))}`
            : "",

        address
            ? `ADR;TYPE=WORK:;;${escapeVCard(address)};;;;`
            : "",

        "END:VCARD"

    ];


    return lines
        .filter(Boolean)
        .join("\r\n");
}


// ============================================================
// ESCAPE VCARD
// ============================================================

function escapeVCard(value) {

    return String(value || "")
        .replace(/\\/g, "\\\\")
        .replace(/\n/g, "\\n")
        .replace(/,/g, "\\,")
        .replace(/;/g, "\\;");
}


// ============================================================
// SAVE CONTACT
// ============================================================

async function saveContact(card) {

    const vcard =
        createVCard(card);


    const blob =
        new Blob(
            [vcard],
            {
                type: "text/vcard;charset=utf-8"
            }
        );


    const url =
        URL.createObjectURL(blob);


    const fullName =
        card.hoTen ||
        card.tenThe ||
        "contact";


    const filename =
        fullName
            .replace(/[^\w\sÀ-ỹ-]/gi, "")
            .replace(/\s+/g, "_") +
        ".vcf";


    /*
     * Nếu điện thoại hỗ trợ Web Share API
     * và cho phép share file vCard
     */

    if (
        navigator.share &&
        navigator.canShare
    ) {

        const file =
            new File(
                [blob],
                filename,
                {
                    type:
                        "text/vcard"
                }
            );


        if (
            navigator.canShare({
                files: [file]
            })
        ) {

            try {

                await navigator.share({
                    files: [file],
                    title: fullName
                });

                URL.revokeObjectURL(url);

                return;

            } catch (error) {

                console.log(
                    "Share contact cancelled:",
                    error
                );

            }

        }

    }


    /*
     * Fallback:
     * tải file VCF
     */

    const link =
        document.createElement("a");

    link.href = url;

    link.download = filename;

    document.body.appendChild(link);

    link.click();

    link.remove();

    setTimeout(
        () => URL.revokeObjectURL(url),
        1000
    );

}


// ============================================================
// RENDER NFC PROFILE
// ============================================================

function renderNFCProfile(card) {

    const items =
        Array.isArray(card.links)
            ? card.links
            : [];


    // ========================================================
    // GENERAL INFORMATION
    // Chỉ kiểm tra các item thuộc phần "Thông tin chung"
    // ========================================================

    const generalItems =
        items.filter(item => {

            const category =
                String(item.category || "")
                    .toUpperCase();

            const value =
                String(item.value || "")
                    .trim();

            return (
                category === "GENERAL" &&
                value !== "" &&
                item.is_active !== false
            );

        });


    // Có ít nhất 1 thông tin chung hay không?
    const hasGeneralInfo =
        generalItems.length > 0;


    const publicUrl =
        getPublicProfileUrl(card);


    document.body.innerHTML = `

        <div class="nfc-page">


            <!-- =========================================
                 COVER
            ========================================== -->

            <div class="nfc-cover">

                ${
                    card.anhBia
                    ?
                    `
                    <img
                        src="${escapeAttr(card.anhBia)}"
                        alt="Ảnh bìa"
                    >
                    `
                    :
                    ""
                }


                <!-- SHARE BUTTON -->

                <button
                    class="nfc-share-top-button"
                    id="nfcShareButton"
                >

                    <span>
                        ↗
                    </span>

                    Chia sẻ

                </button>

            </div>



            <!-- =========================================
                 MAIN
            ========================================== -->

            <div class="nfc-container">


                <!-- AVATAR -->

                ${
                    card.anhDaiDien
                    ?
                    `
                    <img
                        class="nfc-avatar"
                        src="${escapeAttr(card.anhDaiDien)}"
                        alt="Ảnh đại diện"
                    >
                    `
                    :
                    ""
                }



                <!-- LOGO -->

                ${
                    card.logo
                    ?
                    `
                    <img
                        class="nfc-logo"
                        src="${escapeAttr(card.logo)}"
                        alt="Logo"
                    >
                    `
                    :
                    ""
                }



                <!-- NAME -->

                <h1 class="nfc-name">

                    ${escapeHtml(
                        card.hoTen ||
                        card.tenThe ||
                        ""
                    )}

                </h1>



                <!-- POSITION -->

                ${
                    card.chucVu
                    ?
                    `
                    <div class="nfc-position">

                        ${escapeHtml(
                            card.chucVu
                        )}

                    </div>
                    `
                    :
                    ""
                }



                <!-- COMPANY -->

                ${
                    card.congTy
                    ?
                    `
                    <div class="nfc-company">

                        ${escapeHtml(
                            card.congTy
                        )}

                    </div>
                    `
                    :
                    ""
                }



                <!-- DEPARTMENT -->

                ${
                    card.phongBan
                    ?
                    `
                    <div class="nfc-department">

                        ${escapeHtml(
                            card.phongBan
                        )}

                    </div>
                    `
                    :
                    ""
                }



                <!-- INTRO -->

                ${
                    card.gioiThieu
                    ?
                    `
                    <div class="nfc-intro">

                        ${escapeHtml(
                            card.gioiThieu
                        )}

                    </div>
                    `
                    :
                    ""
                }



                <!-- =====================================
                     ALL CARD ITEMS
                ====================================== -->

                <div
                    class="nfc-items"
                >

                    ${renderCardItems(card)}

                </div>



                <!-- =====================================
                     EMPTY
                ====================================== -->

                ${
                    !hasGeneralInfo
                    ?
                    `
                    <div class="nfc-empty-items">

                        Chưa có thông tin liên hệ.

                    </div>
                    `
                    :
                    ""
                }


            </div>



            <!-- =========================================
                 SAVE CONTACT
            ========================================== -->

            <div class="nfc-bottom-bar">

                <button
                    class="nfc-save-contact-button"
                    id="nfcSaveContactButton"
                >

                    <span>
                        👤
                    </span>

                    Lưu danh bạ

                </button>

            </div>


        </div>

    `;


    // ========================================================
    // SHARE BUTTON
    // ========================================================

    const shareButton =
        document.getElementById(
            "nfcShareButton"
        );


    if (shareButton) {

        shareButton.addEventListener(
            "click",
            function () {

                openShareModal(card);

            }
        );

    }


    // ========================================================
    // SAVE CONTACT
    // ========================================================

    const saveContactButton =
        document.getElementById(
            "nfcSaveContactButton"
        );


    if (saveContactButton) {

        saveContactButton.addEventListener(
            "click",
            function () {

                saveContact(card);

            }
        );

    }


    console.log(
        "Rendered NFC profile:",
        card
    );
}


// ============================================================
// INIT
// ============================================================

loadNFCProfile();


window.addEventListener(
    "hashchange",
    loadNFCProfile
);