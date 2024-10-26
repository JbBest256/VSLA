
document.addEventListener('DOMContentLoaded', () => {
    displayCartItems();
    updateCartCount();
});

const currency = 'UGX';

function addToCart(id, name, price, image) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const product = cart.find(item => item.id === id);

    if (product) {
        product.quantity += 1;
    } else {
        cart.push({ id, name, price, quantity: 1, image });
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    displayCartItems();
}

function removeFromCart(id) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart = cart.filter(item => item.id !== id);

    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    displayCartItems();
}

function displayCartItems() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartItemsContainer = document.getElementById('cart-items');
    cartItemsContainer.innerHTML = '';

    cart.forEach(item => {
        const itemRow = document.createElement('tr');
        itemRow.innerHTML = `
            <td class="pe-0">
                <div class="d-flex align-items-center">
                    <img src="${item.image}" class="w-50px h-50px rounded-3 me-3" alt=""/>
                    <span class="fw-bold text-gray-800 cursor-pointer text-hover-primary fs-6 me-1">${item.name}</span>
                </div>
            </td>
            <td class="pe-0">
                <div class="position-relative d-flex align-items-center">
                    <button type="button" class="btn btn-icon btn-sm btn-light btn-icon-gray-500" onclick="decreaseQuantity(${item.id})">
                        <i class="fa fa-minus fs-3x"></i>
                    </button>
                    <input type="text" class="form-control border-0 text-center px-0 fs-3 fw-bold text-gray-800 w-30px" readonly value="${item.quantity}"/>
                    <button type="button" class="btn btn-icon btn-sm btn-light btn-icon-gray-500" onclick="increaseQuantity(${item.id})">
                        <i class="fa fa-plus fs-3x"></i>
                    </button>
                </div>
            </td>
            <td class="text-end">
                <span class="fw-bold text-gray-800 fs-6">${currency}${(item.price * item.quantity).toFixed(2)}</span>
            </td>
        `;
        cartItemsContainer.appendChild(itemRow);
    });

    updateCartSummary();
}

function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cart-count').innerText = cartCount;
}

function updateCartSummary() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const discount = 0; // Add logic for discounts if needed
    const tax = subtotal * 0;
    const total = subtotal - discount + tax;

    document.getElementById('subtotal').innerText = `${currency}${subtotal.toFixed(2)}`;
    document.getElementById('discount').innerText = `${currency}${discount.toFixed(2)}`;
    document.getElementById('tax').innerText = `${currency}${tax.toFixed(2)}`;
    document.getElementById('grand-total').innerText = `${currency}${total.toFixed(2)}`;
}

function clearCart() {
    localStorage.removeItem('cart');
    displayCartItems();
    updateCartCount();
}

function decreaseQuantity(id) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const product = cart.find(item => item.id === id);

    if (product) {
        product.quantity -= 1;
        if (product.quantity <= 0) {
            cart = cart.filter(item => item.id !== id);
        }
        localStorage.setItem('cart', JSON.stringify(cart));
        displayCartItems();
        updateCartCount();
    }
}

function increaseQuantity(id) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const product = cart.find(item => item.id === id);

    if (product) {
        product.quantity += 1;
        localStorage.setItem('cart', JSON.stringify(cart));
        displayCartItems();
        updateCartCount();
    }
}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

