import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import ChartDataLabels from 'chartjs-plugin-datalabels';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels
);

const RevenueByStateChart = ({ data }) => {
  if (!data || !data.states) {
    return (
      <div style={{ 
        height: '400px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        Loading...
      </div>
    );
  }

  // Get top 5 states for better visualization
  const topStates = data.states.slice(0, 5);

  const chartData = {
    labels: topStates.map(state => state.state),
    datasets: [
      {
        label: 'Revenue ($)',
        data: topStates.map(state => state.revenue),
        backgroundColor: 'rgba(75, 192, 192, 0.8)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Revenue by State (Top 5)',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const state = topStates[context.dataIndex];
            return [
              `Revenue: $${context.parsed.y.toLocaleString()}`,
              `Orders: ${state.orders}`,
              `Percentage: ${state.percentage}%`
            ];
          }
        }
      },
      datalabels: {
        anchor: 'end',
        align: 'top',
        formatter: function(value) {
          return '$' + value.toLocaleString(undefined, {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
          });
        },
        font: {
          weight: 'bold',
          size: 10,
        },
        color: '#333',
        rotation: -45,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Revenue ($)',
        },
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          },
        },
      },
      x: {
        title: {
          display: true,
          text: 'State',
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
          font: {
            size: 11,
          },
        },
      },
    },
  };

  return (
    <div className="chart-container">
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default RevenueByStateChart;