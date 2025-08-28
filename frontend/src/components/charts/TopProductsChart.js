import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { getSalesPerformance } from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels
);

const TopProductsChart = () => {
  const [chartData, setChartData] = useState(null);
  const [sellerName, setSellerName] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getSalesPerformance();
        setSellerName(data.seller_name);
        
        // Get top 5 products by revenue
        const topProducts = data.revenue_by_product.slice(0, 5);
        const productNames = topProducts.map(item => {
          // Truncate long product names for better display
          return item.name.length > 20 ? item.name.substring(0, 20) + '...' : item.name;
        });
        const revenues = topProducts.map(item => item.revenue);

        setChartData({
          labels: productNames,
          datasets: [
            {
              label: 'Revenue',
              data: revenues,
              backgroundColor: 'rgba(75, 192, 192, 0.8)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 2,
            },
          ],
        });
      } catch (error) {
        console.error('Failed to fetch top products data:', error);
      }
    };

    fetchData();
  }, []);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Top 5 Products by Revenue - ${sellerName}`,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.label}: $${context.parsed.y.toLocaleString()}`;
          }
        }
      },
      datalabels: {
        display: true,
        align: 'top',
        anchor: 'end',
        color: '#333',
        font: {
          weight: 'bold',
          size: 11,
        },
        formatter: function(value) {
          return '$' + value.toLocaleString(undefined, {maximumFractionDigits: 0});
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      }
    }
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      {chartData ? (
        <Bar data={chartData} options={options} />
      ) : (
        <div>Loading top products chart...</div>
      )}
    </div>
  );
};

export default TopProductsChart;