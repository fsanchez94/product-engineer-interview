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
import { getMarketShare } from '../../services/api';
import { useSeller } from '../../contexts/SellerContext';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels
);

const MarketShareChart = () => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { selectedSeller } = useSeller();

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedSeller?.seller_id) return;
      
      try {
        setLoading(true);
        const data = await getMarketShare(selectedSeller.seller_id);
        
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
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedSeller?.seller_id]);

  const options = {
    responsive: true,
    indexAxis: 'y', // This makes it a horizontal bar chart
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Market Share by Category - ${selectedSeller?.name || 'Loading...'}`,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed.x.toFixed(1)}%`;
          }
        }
      },
      datalabels: {
        display: true,
        align: 'end',
        anchor: 'end',
        color: '#333',
        font: {
          weight: 'bold',
          size: 12,
        },
        formatter: function(value) {
          return value.toFixed(1) + '%';
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
      {loading ? (
        <div>Loading market share chart...</div>
      ) : chartData ? (
        <Bar data={chartData} options={options} />
      ) : (
        <div>No market share data available</div>
      )}
    </div>
  );
};

export default MarketShareChart;