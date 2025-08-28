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
import { getMarketShare } from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const MarketShareChart = () => {
  const [chartData, setChartData] = useState(null);
  const [sellerName, setSellerName] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getMarketShare();
        setSellerName(data.seller_name);
        
        const categories = data.category_market_share.map(item => item.category);
        const shares = data.category_market_share.map(item => item.share_percentage);

        setChartData({
          labels: categories,
          datasets: [
            {
              label: 'Market Share (%)',
              data: shares,
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 2,
            },
          ],
        });
      } catch (error) {
        console.error('Failed to fetch market share data:', error);
      }
    };

    fetchData();
  }, []);

  const options = {
    responsive: true,
    indexAxis: 'y', // This makes it a horizontal bar chart
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Market Share by Category - ${sellerName}`,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed.x.toFixed(1)}%`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      }
    }
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      {chartData ? (
        <Bar data={chartData} options={options} />
      ) : (
        <div>Loading market share chart...</div>
      )}
    </div>
  );
};

export default MarketShareChart;