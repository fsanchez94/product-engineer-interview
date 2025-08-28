import React, { useState, useEffect } from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';
import { getSalesPerformance } from '../../services/api';

ChartJS.register(ArcElement, Tooltip, Legend, Title);

const CategoryChart = () => {
  const [chartData, setChartData] = useState(null);
  const [sellerName, setSellerName] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getSalesPerformance();
        setSellerName(data.seller_name);
        
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
      }
    };

    fetchData();
  }, []);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: `Revenue by Category - ${sellerName}`,
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
      }
    },
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      {chartData ? (
        <Pie data={chartData} options={options} />
      ) : (
        <div>Loading category chart...</div>
      )}
    </div>
  );
};

export default CategoryChart;