let cart = JSON.parse(localStorage.getItem('cart')) || [];
  let discountApplied = false; // Biến kiểm tra mã giảm giá

  // Danh sách mã giảm giá hợp lệ (có thể thêm mới)
  const validDiscountCodes = ['VW2CIIED', '8VEG7YJS', 'UACKTVUZ', 'AGHX7V1D', '2EQZKB30',
                              '5DCB7KFI', 'PZCMHCDU', 'BF35UP2A', '6VGR7B3W', '9TUSKZ1H',
                              'PFMX1PIK', '9TBJ57TI', 'AMNCVZN4', 'LC5N4XDN', 'AYHZP8DI', 
                              'XZUNXC2I', '866OI4MG', 'VV4NI9U8', 'B3JSDXIC', 'V4RWNCY2', 
                              '4DFIIFV8', 'S0UTHJL2', '9VOM67D3', 'DK9XKIMZ', '4LSZHPFH', 
                              '8NX0Y8EF', 'HJ9TCIAW', 'ODKYBEXA', 'E0JGK70L', 'HHI5SH3R', 
                              'NZ4KCWI8', 'T75FI9UN', 'I9KY3321', 'DRBTIG22', 'BS7ON9PH', 
                              '7P8SJNNI', 'DVTBNIXW', 'EK9ZNAIJ', 'FLQT07GP', '9D7CBFWJ', 
                              'TPPRDCA1', '816O08Y4', 'PJ0KQ9LH', 'MMAOMWSJ', 'IUPLAD0T', 
                              'HA45EE6Y', 'GJN0QI64', '61D1N5VA', '15Y5BYY9', 'AQ0ED04H'];

  // Lấy mã đã dùng từ localStorage
  let usedDiscounts = JSON.parse(localStorage.getItem('usedDiscounts')) || [];

  const exportBtn = document.getElementById('exportBtn');
  const discountSection = document.getElementById('discountSection');
  const discountCodeInput = document.getElementById('discountCode');
  const applyDiscountBtn = document.getElementById('applyDiscountBtn');
  const discountMessage = document.getElementById('discountMessage');
  const closeDiscountBtn = document.getElementById('closeDiscount');
  
  exportBtn.addEventListener('click', function() {
    if (cart.length === 0) {
      // Nếu giỏ hàng trống, thông báo ngay lập tức
      alert('Giỏ hàng của bạn đang trống.');
    } else {
      const applyDiscount = confirm("Bạn có muốn áp mã giảm giá không?");
      
      if (applyDiscount) {
        // Hiển thị khung nhập mã giảm giá
        discountSection.style.display = 'block';
        
        // Xử lý đóng khung mã giảm giá
        closeDiscountBtn.addEventListener('click', function() {
          discountSection.style.display = 'none';
        });

        // Xử lý nút áp dụng mã giảm giá
        applyDiscountBtn.addEventListener('click', function() {
          const enteredCode = discountCodeInput.value.trim();

          // Kiểm tra mã hợp lệ và mã chưa được sử dụng
          if (validDiscountCodes.includes(enteredCode) && !usedDiscounts.includes(enteredCode)) {
            discountApplied = true; // Đánh dấu đã áp dụng mã giảm giá
            discountMessage.style.color = "green";
            discountMessage.innerText = "Mã giảm giá đã được áp dụng!";
            
            // Lưu mã vào danh sách mã đã dùng
            usedDiscounts.push(enteredCode);
            localStorage.setItem('usedDiscounts', JSON.stringify(usedDiscounts));

            // Sau khi áp dụng mã giảm giá, gọi hàm xuất file với giá giảm
            exportOrder(true);
            discountSection.style.display = 'none'; // Ẩn khung giảm giá sau khi áp dụng
          } else {
            discountMessage.innerText = "Mã giảm giá không hợp lệ hoặc đã được sử dụng!";
            exportOrder(false);
            discountSection.style.display = 'none'; // Ẩn khung giảm giá nếu mã không hợp lệ
          }
        });
      } else {
        exportOrder(false); // Xuất file bình thường nếu không áp dụng giảm giá
      }
    }
  });

  // Hàm xuất file với tùy chọn giảm giá
  function exportOrder(applyDiscount) {
    if (cart.length > 0) {
      let orderInfo = '<h2 style="text-align: center;">Thông tin đơn hàng của bạn</h2><br>';
      let totalAmount = 0;

      cart.forEach((item, index) => {
        let price = typeof item.price === 'string' 
          ? parseFloat(item.price.replace(/[^\d.-]/g, '')) 
          : parseFloat(item.price);

        let itemTotal = price * item.quantity;
        totalAmount += itemTotal;

        orderInfo += `<p><strong>${index + 1}. ${item.name} ${item.unit}</strong></p>`;
        orderInfo += `<p>Số lượng: ${item.quantity}</p>`;
        orderInfo += `<p>Giá tiền: ${price.toLocaleString('vi-VN')}đ</p>`;
        orderInfo += `<p>Thành tiền: ${itemTotal.toLocaleString('vi-VN')}đ</p>`;
        orderInfo += `<p>Thêm vào lúc: ${item.addedTime}</p>`;
        orderInfo += `<hr>`;
      });

      if (applyDiscount) {
        totalAmount -= 100000; // Giảm 100.000 VND
        orderInfo += `<h3 style="text-align: center;">Tổng số tiền: ${totalAmount.toLocaleString('vi-VN')}đ (đã áp dụng cho mã giảm giá)</h3>`;
      } else {
        orderInfo += `<h3 style="text-align: center;">Tổng số tiền: ${totalAmount.toLocaleString('vi-VN')}đ</h3>`;
      }

      const orderInfoContainer = document.getElementById('orderInfoContainer');
      orderInfoContainer.innerHTML = orderInfo;
      orderInfoContainer.style.display = 'block';

      html2canvas(orderInfoContainer, { scale: 2 }).then(function(canvas) {
        const link = document.createElement('a');
        link.download = 'don_hang.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
        orderInfoContainer.style.display = 'none';
      });
    }
  }

  const resetCartBtn = document.getElementById('resetCartBtn');
  resetCartBtn.addEventListener('click', function() {
    const confirmation = confirm("Toàn bộ sản phẩm trong giỏ hàng sẽ bị mất. Bạn có muốn tiếp tục không?");
    
    if (confirmation) {
      cart = [];
      localStorage.setItem('cart', JSON.stringify(cart));
      alert('Giỏ hàng đã được reset.');
      document.getElementById('cartContent').innerHTML = ''; 
    } else {
      alert('Giỏ hàng không bị reset.');
    }
  });

  // Reset giỏ hàng mỗi khi tải lại trang
  window.onload = function() {
    localStorage.removeItem('cart');
  };

  function toggleQR() {
    var qrCode = document.getElementById('qr-code');
    var qrToggle = document.getElementById('qr-toggle');
    if (qrCode.style.display === 'none') {
      qrCode.style.display = 'block';
      qrToggle.innerText = 'Ẩn ảnh QR';
    } else {
      qrCode.style.display = 'none';
      qrToggle.innerText = 'Hiển thị ảnh QR chuyển khoản';
    }
  }

  function zoomQR() {
    var qrCode = document.getElementById('qr-code');
    if (qrCode.style.transform === 'scale(3.5)') {
      qrCode.style.transform = 'scale(1)';
    } else {
      qrCode.style.transform = 'scale(3.5)';
    }
  }