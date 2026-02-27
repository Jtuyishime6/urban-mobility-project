// Urban Mobility Dashboard JavaScript
// API Configuration
const API_BASE = 'http://localhost:5000/api';

// State
let currentPage = 1;
let currentFilters = {};
let charts = {};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  checkAPIHealth();
  loadBoroughs();
  loadSummaryStats();
  loadCharts();
  loadTrips();
});

// Check API health
async function checkAPIHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (response.ok) {
      document.getElementById('status-text').textContent = 'Connected';
      document.getElementById('status-dot').style.background = '#10b981';
    } else {
      throw new Error('API unhealthy');
    }
  } catch (error) {
    document.getElementById('status-text').textContent = 'Disconnected';
    document.getElementById('status-dot').style.background = '#ef4444';
    console.error('API health check failed:', error);
  }
}

// Load boroughs for filter dropdown
async function loadBoroughs() {
  try {
    const response = await fetch(`${API_BASE}/zones/boroughs`);
    const result = await response.json();
    
    const select = document.getElementById('filter-borough');
    result.data.forEach(borough => {
      const option = document.createElement('option');
      option.value = borough;
      option.textContent = borough;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('Failed to load boroughs:', error);
  }
}

// Load summary statistics
async function loadSummaryStats() {
  try {
    const response = await fetch(`${API_BASE}/trips/summary`);
    const stats = await response.json();
    
    document.getElementById('stat-total-trips').textContent = stats.total_trips.toLocaleString();
    document.getElementById('stat-avg-fare').textContent = `$${stats.avg_fare.toFixed(2)}`;
    document.getElementById('stat-avg-distance').textContent = `${stats.avg_distance.toFixed(2)} mi`;
    document.getElementById('stat-avg-speed').textContent = `${stats.avg_speed.toFixed(1)} mph`;
  } catch (error) {
    console.error('Failed to load summary stats:', error);
  }
}

// Load all charts
async function loadCharts() {
  await loadHourlyChart();
  await loadRevenueChart();
  await loadFareChart();
  await loadZonesChart();
}

// Hourly demand chart
async function loadHourlyChart() {
  try {
    const response = await fetch(`${API_BASE}/analytics/hourly-demand`);
    const result = await response.json();
    
    const ctx = document.getElementById('chart-hourly').getContext('2d');
    
    if (charts.hourly) charts.hourly.destroy();
    
    charts.hourly = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: result.data.map(d => `${d.pickup_hour}:00`),
        datasets: [{
          label: 'Trips',
          data: result.data.map(d => d.trip_count),
          backgroundColor: '#3b82f6',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false }
        }
      }
    });
  } catch (error) {
    console.error('Failed to load hourly chart:', error);
  }
}

// Revenue by borough chart
async function loadRevenueChart() {
  try {
    const response = await fetch(`${API_BASE}/analytics/revenue-by-zone`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const result = await response.json();
    
    if (!result.data || result.data.length === 0) {
      console.warn('No revenue data available');
      return;
    }
    
    const ctx = document.getElementById('chart-revenue').getContext('2d');
    
    if (charts.revenue) charts.revenue.destroy();
    
    charts.revenue = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: result.data.map(d => d.borough_name),
        datasets: [{
          data: result.data.map(d => parseFloat(d.total_revenue) || 0),
          backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true
      }
    });
  } catch (error) {
    console.error('Failed to load revenue chart:', error);
  }
}

// Fare by distance chart
async function loadFareChart() {
  try {
    const response = await fetch(`${API_BASE}/analytics/average-fare-per-mile`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const result = await response.json();
    
    if (!result.data || result.data.length === 0) {
      console.warn('No fare data available');
      return;
    }
    
    const ctx = document.getElementById('chart-fare').getContext('2d');
    
    if (charts.fare) charts.fare.destroy();
    
    charts.fare = new Chart(ctx, {
      type: 'line',
      data: {
        labels: result.data.map(d => d.distance_group),
        datasets: [{
          label: 'Avg Fare ($)',
          data: result.data.map(d => parseFloat(d.avg_fare) || 0),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true
      }
    });
  } catch (error) {
    console.error('Failed to load fare chart:', error);
  }
}

// Top zones chart
async function loadZonesChart() {
  try {
    const response = await fetch(`${API_BASE}/analytics/top-revenue-zones?n=10`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const result = await response.json();
    
    if (!result.data || result.data.length === 0) {
      console.warn('No zones data available');
      return;
    }
    
    const ctx = document.getElementById('chart-zones').getContext('2d');
    
    if (charts.zones) charts.zones.destroy();
    
    charts.zones = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: result.data.map(d => d.zone_name),
        datasets: [{
          label: 'Revenue ($)',
          data: result.data.map(d => parseFloat(d.total_revenue) || 0),
          backgroundColor: '#8b5cf6'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        indexAxis: 'y',
        plugins: {
          legend: { display: false }
        }
      }
    });
  } catch (error) {
    console.error('Failed to load zones chart:', error);
  }
}

// Load trips table
async function loadTrips(page = 1) {
  const tbody = document.getElementById('trips-tbody');
  
  try {
    // Show loading state
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Loading trips...</td></tr>';
    
    const params = new URLSearchParams({
      page: page,
      limit: 50,
      ...currentFilters
    });
    
    const response = await fetch(`${API_BASE}/trips?${params}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    tbody.innerHTML = '';
    
    if (!result.data || result.data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No trips found</td></tr>';
      document.getElementById('btn-prev').disabled = true;
      document.getElementById('btn-next').disabled = true;
      return;
    }
    
    result.data.forEach(trip => {
      const row = document.createElement('tr');
      
      // Helper function to safely format numbers
      const formatNum = (val, decimals = 2) => {
        if (val === null || val === undefined || val === '') return 'N/A';
        const num = parseFloat(val);
        return isNaN(num) ? 'N/A' : num.toFixed(decimals);
      };
      
      row.innerHTML = `
        <td>${new Date(trip.pickup_datetime).toLocaleString()}</td>
        <td>${trip.pickup_zone || 'N/A'}</td>
        <td>${trip.dropoff_zone || 'N/A'}</td>
        <td>${trip.pickup_borough || 'N/A'}</td>
        <td>${formatNum(trip.trip_distance, 2)} mi</td>
        <td>$${formatNum(trip.fare_amount, 2)}</td>
        <td>$${formatNum(trip.total_amount, 2)}</td>
        <td>${trip.trip_duration_minutes ? formatNum(trip.trip_duration_minutes, 0) + ' min' : 'N/A'}</td>
      `;
      tbody.appendChild(row);
    });
    
    currentPage = page;
    document.getElementById('page-display').textContent = `Page ${page}`;
    document.getElementById('btn-prev').disabled = page === 1;
    document.getElementById('btn-next').disabled = result.data.length < 50;
    
  } catch (error) {
    console.error('Failed to load trips:', error);
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:#ef4444;">
      Error loading trips. Make sure the backend is running on http://localhost:5000
      <br><small>Error: ${error.message}</small>
    </td></tr>`;
    document.getElementById('btn-prev').disabled = true;
    document.getElementById('btn-next').disabled = true;
  }
}

// Apply filters
function applyFilters() {
  currentFilters = {};
  
  const startDate = document.getElementById('filter-start-date').value;
  const endDate = document.getElementById('filter-end-date').value;
  const borough = document.getElementById('filter-borough').value;
  const minFare = document.getElementById('filter-min-fare').value;
  const maxFare = document.getElementById('filter-max-fare').value;
  const minDistance = document.getElementById('filter-min-distance').value;
  
  if (startDate) currentFilters.start_date = startDate;
  if (endDate) currentFilters.end_date = endDate;
  if (borough) currentFilters.pickup_zone = borough;
  if (minFare) currentFilters.min_fare = minFare;
  if (maxFare) currentFilters.max_fare = maxFare;
  if (minDistance) currentFilters.min_distance = minDistance;
  
  loadTrips(1);
}

// Reset filters
function resetFilters() {
  document.getElementById('filter-start-date').value = '2019-01-01';
  document.getElementById('filter-end-date').value = '2019-01-31';
  document.getElementById('filter-borough').value = '';
  document.getElementById('filter-min-fare').value = '';
  document.getElementById('filter-max-fare').value = '';
  document.getElementById('filter-min-distance').value = '';
  
  currentFilters = {};
  loadTrips(1);
}

// Change page
function changePage(delta) {
  loadTrips(currentPage + delta);
}