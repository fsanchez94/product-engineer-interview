import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { getSellerAnalytics } from '../../services/api';
import { useSeller } from '../../contexts/SellerContext';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels
);

const RevenueChart = () => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { selectedSeller } = useSeller();

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedSeller?.seller_id) return;
      
      try {
        setLoading(true);
        const data = await getSellerAnalytics(selectedSeller.seller_id);
        
        // For now, create a simple representation with the current revenue
        // In a real implementation, we'd need time-series data
        const mockDays = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        const revenue = data.revenue;
        const mockRevenue = [
          revenue * 0.2,
          revenue * 0.3,
          revenue * 0.25,
          revenue * 0.25
        ];

        setChartData({
          labels: mockDays,
          datasets: [
            {
              label: 'Revenue',
              data: mockRevenue,
              borderColor: 'rgb(75, 192, 192)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              tension: 0.1,
            },
          ],
        });
      } catch (error) {
        console.error('Failed to fetch revenue data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedSeller?.seller_id]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Revenue Trends - ${selectedSeller?.name || 'Loading...'}`,
      },
      datalabels: {
        display: true,
        align: 'top',
        anchor: 'end',
        color: '#333',
        font: {
          weight: 'bold',
          size: 12,
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
      }
    }
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      {loading ? (
        <div>Loading revenue chart...</div>
      ) : chartData ? (
        <Line data={chartData} options={options} />
      ) : (
        <div>No revenue data available</div>
      )}
    </div>
  );
};

export default RevenueChart;