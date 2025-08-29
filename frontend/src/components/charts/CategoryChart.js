import React, { useState, useEffect } from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { getSalesPerformance } from '../../services/api';
import { useSeller } from '../../contexts/SellerContext';

ChartJS.register(ArcElement, Tooltip, Legend, Title, ChartDataLabels);

const CategoryChart = () => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { selectedSeller } = useSeller();

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedSeller?.seller_id) return;
      
      try {
        setLoading(true);
        const data = await getSalesPerformance(selectedSeller.seller_id);
        
        const categories = data.revenue_by_category.map(item => item.category);
        const revenues = data.revenue_by_category.map(item => item.revenue);
        
        const colors = [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
        ];

        setChartData({
          labels: categories,
          datasets: [
            {
              label: 'Revenue by Category',
              data: revenues,
              backgroundColor: colors.slice(0, categories.length),
              borderColor: colors.slice(0, categories.length).map(color => 
                color.replace('0.8', '1')
              ),
              borderWidth: 2,
            },
          ],
        });
      } catch (error) {
        console.error('Failed to fetch category data:', error);
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
        position: 'right',
      },
      title: {
        display: true,
        text: `Revenue by Category - ${selectedSeller?.name || 'Loading...'}`,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${context.label}: $${value.toLocaleString()} (${percentage}%)`;
          }
        }
      },
      datalabels: {
        display: true,
        color: 'white',
        font: {
          weight: 'bold',
          size: 12,
        },
        formatter: function(value, context) {
          const total = context.dataset.data.reduce((a, b) => a + b, 0);
          const percentage = ((value / total) * 100).toFixed(1);
          return percentage + '%';
        }
      }
    },
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      {loading ? (
        <div>Loading category chart...</div>
      ) : chartData ? (
        <Pie data={chartData} options={options} />
      ) : (
        <div>No category data available</div>
      )}
    </div>
  );
};

export default CategoryChart;