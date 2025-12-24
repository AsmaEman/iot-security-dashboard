import React from 'react';
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

const KPICard = ({ title, value, icon, color = 'primary', trend }) => {
  const isPositiveTrend = trend && (trend.includes('+') || trend.includes('improvement'));

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={`${color}.main`}>
              {value}
            </Typography>
            {trend && (
              <Box display="flex" alignItems="center" mt={1}>
                {isPositiveTrend ? (
                  <TrendingUp color="success" fontSize="small" />
                ) : (
                  <TrendingDown color="error" fontSize="small" />
                )}
                <Typography
                  variant="caption"
                  color={isPositiveTrend ? 'success.main' : 'error.main'}
                  ml={0.5}
                >
                  {trend}
                </Typography>
              </Box>
            )}
          </Box>
          <Avatar sx={{ bgcolor: `${color}.main`, width: 56, height: 56 }}>
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );
};

export default KPICard;