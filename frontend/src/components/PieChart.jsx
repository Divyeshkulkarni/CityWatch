import React from 'react';
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const PieChart = ({ data, title, colors = ['#00D9FF', '#00FF88', '#FFD700', '#FF6B6B', '#9B59B6'], showCenterLabel = false, textColor = 'white' }) => {
  const RADIAN = Math.PI / 180;
  
  const total = data.reduce((sum, item) => sum + item.value, 0);
  
  const CustomLegend = ({ payload }) => {
    const firstColumn = payload.slice(0, 3);
    const secondColumn = payload.slice(3, 5);

    const renderColumn = (column) => (
      <div className="flex flex-col gap-2 items-start">
        {column.map((entry, index) => (
          <div key={`item-${index}`} className="flex items-center gap-2 cursor-pointer">
            <div style={{ width: 10, height: 10, backgroundColor: entry.color, borderRadius: '50%' }} />
            <span className={`text-${textColor} text-xs`}>{entry.value}</span>
          </div>
        ))}
      </div>
    );

    return (
      <div className="flex justify-center gap-8 mt-6">
        {renderColumn(firstColumn)}
        {renderColumn(secondColumn)}
      </div>
    );
  };
  
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    // Don't show labels on segments if center label is enabled
    if (showCenterLabel) return null;
    
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill={textColor}
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-xs font-bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-deep-blue border border-electric-blue border-opacity-50 rounded-lg p-3 shadow-xl">
          <p className="text-electric-blue font-semibold">{payload[0].name}</p>
          <p className={`text-${textColor} font-bold`}>{payload[0].value}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className={`text-sm font-bold text-${textColor} uppercase tracking-wider mb-4 text-center`}>
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={350}>
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            innerRadius={showCenterLabel ? 60 : 40}
            outerRadius={showCenterLabel ? 100 : 80}
            fill="#8884d8"
            dataKey="value"
            animationBegin={0}
            animationDuration={800}
            animationEasing="ease-out"
            paddingAngle={2}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={colors[index % colors.length]}
                style={{ 
                  filter: 'drop-shadow(0 0 8px rgba(0, 217, 255, 0.3))',
                  transition: 'opacity 0.3s'
                }}
              />
            ))}
          </Pie>
          {showCenterLabel && (
            <>
              <text
                x="50%"
                y="45%"
                textAnchor="middle"
                dominantBaseline="middle"
                className="font-semibold"
                style={{ fill: textColor, fontSize: '12px' }}
              >
                Total Vehicles
              </text>
              <text
                x="50%"
                y="58%"
                textAnchor="middle"
                dominantBaseline="middle"
                className={`text-${textColor} font-bold`}
                style={{ fontSize: '28px' }}
              >
                {total}
              </text>
            </>
          )}
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PieChart;
