"use client"

import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Typography } from '@mui/material';
import { toast } from 'react-toastify';

const WarehouseDetailsDialog = React.forwardRef((props, ref) => {
  const [open, setOpen] = React.useState(false);
  const [warehouse, setWarehouse] = React.useState<any>(null);
  const [sales, setSales] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState<boolean>(false);

  React.useImperativeHandle(ref, () => ({
    handleClickOpen(warehouseData: any) {
        setWarehouse(warehouseData);
        fetchSales(warehouseData.name);
        setOpen(true);
    }
  }));

  const handleClose = () => {
    setOpen(false);
  }

  const fetchSales = async (warehouseName: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/sales-by-warehouse?warehouseName=${encodeURIComponent(warehouseName)}`);
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      const data = await response.json();
      setSales(data.sales);
    } catch (error) {
      toast.error('Error fetching sales data.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <React.Fragment>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="warehouse-dialog-title"
        aria-describedby="warehouse-dialog-description"
        maxWidth="md"
        fullWidth
      >
        <DialogTitle id="warehouse-dialog-title">
          {"Warehouse Details"}
        </DialogTitle>
        <DialogContent>
          {warehouse && (
            <Box>
              <Typography variant="h6">Warehouse Information</Typography>
              <Typography variant="body1">ID: {warehouse.id}</Typography>
              <Typography variant="body1">Name: {warehouse.name}</Typography>
              <Typography variant="body1">Latitude: {warehouse.latitude}</Typography>
              <Typography variant="body1">Longitude: {warehouse.longitude}</Typography>
              <Typography variant="h6" sx={{ mt: 2 }}>Sales</Typography>
              {loading ? (
                <Typography variant="body2">Searching for sales...</Typography>
              ) : sales.length > 0 ? (
                sales.map((sale, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Typography variant="body2">ID: {sale.id}</Typography>
                    <Typography variant="body2">Date: {sale.date}</Typography>
                    <Typography variant="body2">Client Type: {sale.client_type}</Typography>
                    <Typography variant="body2">Product Line: {sale.product_line}</Typography>
                    <Typography variant="body2">Quantity: {sale.quantity}</Typography>
                    <Typography variant="body2">Unit Price: {sale.unit_price}</Typography>
                    <Typography variant="body2">Total: {sale.total}</Typography>
                    <Typography variant="body2">Payment: {sale.payment}</Typography>
                  </Box>
                ))
              ) : (
                <Typography variant="body2">No sales data available.</Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
})

export default WarehouseDetailsDialog;