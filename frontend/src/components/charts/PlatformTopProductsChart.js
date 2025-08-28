import React from 'react';

const PlatformTopProductsChart = ({ data }) => {
  if (!data || !data.top_products) {
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

  // Get top 10 products
  const topProducts = data.top_products.slice(0, 10);

  return (
    <div className="chart-container">
      <div style={{ padding: '20px' }}>
        <h3 style={{ 
          margin: '0 0 20px 0', 
          textAlign: 'center', 
          fontSize: '16px', 
          fontWeight: 'bold' 
        }}>
          Top 10 Products by Revenue
        </h3>
        
        <div style={{ 
          maxHeight: '350px', 
          overflowY: 'auto',
          border: '1px solid #dee2e6',
          borderRadius: '8px'
        }}>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse',
            fontSize: '14px'
          }}>
            <thead>
              <tr style={{ 
                backgroundColor: '#f8f9fa',
                borderBottom: '2px solid #dee2e6',
                position: 'sticky',
                top: 0
              }}>
                <th style={{ 
                  padding: '12px 8px', 
                  textAlign: 'left',
                  fontWeight: 'bold',
                  width: '10%'
                }}>
                  #
                </th>
                <th style={{ 
                  padding: '12px 8px', 
                  textAlign: 'left',
                  fontWeight: 'bold',
                  width: '45%'
                }}>
                  Product Name
                </th>
                <th style={{ 
                  padding: '12px 8px', 
                  textAlign: 'left',
                  fontWeight: 'bold',
                  width: '20%'
                }}>
                  Category
                </th>
                <th style={{ 
                  padding: '12px 8px', 
                  textAlign: 'right',
                  fontWeight: 'bold',
                  width: '15%'
                }}>
                  Revenue
                </th>
                <th style={{ 
                  padding: '12px 8px', 
                  textAlign: 'right',
                  fontWeight: 'bold',
                  width: '10%'
                }}>
                  Sold
                </th>
              </tr>
            </thead>
            <tbody>
              {topProducts.map((product, index) => (
                <tr key={product.product_id} style={{
                  borderBottom: '1px solid #dee2e6',
                  backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa'
                }}>
                  <td style={{ 
                    padding: '10px 8px',
                    fontWeight: 'bold',
                    color: '#007bff'
                  }}>
                    {index + 1}
                  </td>
                  <td style={{ 
                    padding: '10px 8px',
                    fontWeight: '500'
                  }}>
                    {product.name}
                  </td>
                  <td style={{ 
                    padding: '10px 8px',
                    color: '#6c757d'
                  }}>
                    {product.category}
                  </td>
                  <td style={{ 
                    padding: '10px 8px',
                    textAlign: 'right',
                    fontWeight: 'bold',
                    color: '#28a745'
                  }}>
                    ${product.revenue.toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2
                    })}
                  </td>
                  <td style={{ 
                    padding: '10px 8px',
                    textAlign: 'right',
                    fontWeight: '500'
                  }}>
                    {product.quantity_sold}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PlatformTopProductsChart;