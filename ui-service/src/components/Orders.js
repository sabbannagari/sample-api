import React, { useState, useEffect } from 'react';
import { orderAPI } from '../services/api';
import './Orders.css';

function Orders({ user }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    user_id: '',
    shipping_address: '',
    items: [{ product_id: '', product_name: '', quantity: '', price: '' }]
  });

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await orderAPI.getAll();
      setOrders(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch orders');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setFormData({
      user_id: '',
      shipping_address: '',
      items: [{ product_id: '', product_name: '', quantity: '', price: '' }]
    });
    setShowModal(true);
  };

  const handleAddItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { product_id: '', product_name: '', quantity: '', price: '' }]
    });
  };

  const handleRemoveItem = (index) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index][field] = value;
    setFormData({ ...formData, items: newItems });
  };

  const handleCancel = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) {
      return;
    }
    try {
      await orderAPI.cancel(orderId);
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to cancel order');
    }
  };

  const handleDelete = async (orderId) => {
    if (!window.confirm('Are you sure you want to delete this order?')) {
      return;
    }
    try {
      await orderAPI.delete(orderId);
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete order');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const orderData = {
        ...formData,
        user_id: parseInt(formData.user_id),
        items: formData.items.map(item => ({
          ...item,
          product_id: parseInt(item.product_id),
          quantity: parseInt(item.quantity),
          price: parseFloat(item.price)
        }))
      };
      await orderAPI.create(orderData);
      setShowModal(false);
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create order');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#ff9800',
      processing: '#2196F3',
      shipped: '#9C27B0',
      delivered: '#4CAF50',
      cancelled: '#f44336'
    };
    return colors[status] || '#666';
  };

  return (
    <div className="orders-container">
      <div className="orders-header">
        <h1>Order Management</h1>
        <button onClick={handleCreate} className="btn-primary">
          + Create Order
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading">Loading orders...</div>
      ) : (
        <div className="orders-list">
          {orders.map((order) => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <div>
                  <h3>Order #{order.id}</h3>
                  <span className="order-date">
                    {new Date(order.created_at).toLocaleDateString()}
                  </span>
                </div>
                <span
                  className="order-status"
                  style={{ backgroundColor: getStatusColor(order.status) }}
                >
                  {order.status.toUpperCase()}
                </span>
              </div>

              <div className="order-details">
                <div className="detail-row">
                  <span className="label">User ID:</span>
                  <span>{order.user_id}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Total Amount:</span>
                  <span className="total-amount">${order.total_amount.toFixed(2)}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Shipping Address:</span>
                  <span>{order.shipping_address}</span>
                </div>
              </div>

              <div className="order-items">
                <h4>Items:</h4>
                {order.items.map((item, index) => (
                  <div key={index} className="order-item">
                    <span>{item.product_name}</span>
                    <span>Qty: {item.quantity} × ${item.price.toFixed(2)}</span>
                  </div>
                ))}
              </div>

              <div className="order-actions">
                {order.status !== 'cancelled' && order.status !== 'delivered' && (
                  <button onClick={() => handleCancel(order.id)} className="btn-cancel-order">
                    Cancel Order
                  </button>
                )}
                <button onClick={() => handleDelete(order.id)} className="btn-delete">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create Order</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>User ID *</label>
                <input
                  type="number"
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Shipping Address *</label>
                <textarea
                  value={formData.shipping_address}
                  onChange={(e) => setFormData({ ...formData, shipping_address: e.target.value })}
                  rows="2"
                  required
                />
              </div>

              <h4>Items</h4>
              {formData.items.map((item, index) => (
                <div key={index} className="item-group">
                  <div className="item-header">
                    <span>Item {index + 1}</span>
                    {formData.items.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveItem(index)}
                        className="btn-remove-item"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Product ID *</label>
                      <input
                        type="number"
                        value={item.product_id}
                        onChange={(e) => handleItemChange(index, 'product_id', e.target.value)}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Product Name *</label>
                      <input
                        type="text"
                        value={item.product_name}
                        onChange={(e) => handleItemChange(index, 'product_name', e.target.value)}
                        required
                      />
                    </div>
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Quantity *</label>
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Price *</label>
                      <input
                        type="number"
                        step="0.01"
                        value={item.price}
                        onChange={(e) => handleItemChange(index, 'price', e.target.value)}
                        required
                      />
                    </div>
                  </div>
                </div>
              ))}

              <button type="button" onClick={handleAddItem} className="btn-add-item">
                + Add Item
              </button>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn-cancel">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Create Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Orders;
