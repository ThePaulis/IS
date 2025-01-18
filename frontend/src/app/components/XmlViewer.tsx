"use client"

import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Tab, Tabs, TextField } from '@mui/material';
import { Search } from '@mui/icons-material';
import { toast, ToastContainer } from 'react-toastify';
import xmlFormatter from 'xml-formatter';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function CustomTabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;
  
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`simple-tabpanel-${index}`}
        aria-labelledby={`simple-tab-${index}`}
        {...other}
      >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
      </div>
    );
}

function a11yProps(index: number) {
    return {
      id: `simple-tab-${index}`,
      'aria-controls': `simple-tabpanel-${index}`,
    };
}

const XmlViewerDialog = React.forwardRef((_, ref) => {
  const [open, setOpen]     = React.useState(false)
  const [value, setValue]   = React.useState(0);
  const [xml_filtered_by_warehouse, setXmlFilteredByWarehouse] = React.useState<string>("<Sales></Sales>");
  const [xml_filtered_by_payment, setXmlFilteredByPayment] = React.useState<string>("<Sales></Sales>");
  const [xml_filtered_by_product_line, setXmlFilteredByProductLine] = React.useState<string>("<Sales></Sales>");

  const [searchByWarehouseForm, setSearchByWarehouseForm]  = React.useState({
    warehouse: ''
  });

  const [searchByPaymentForm, setSearchByPaymentForm]  = React.useState({
    payment: ''
  });

  const [searchByProductLineForm, setSearchByProductLineForm]  = React.useState({
    product_line: ''
  });

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  React.useImperativeHandle(ref, () => ({
    handleClickOpen() {
        setOpen(true)
    }
  }));

  const handleClose = () => {
    setOpen(false);
  };

  const handleSubmitWarehouse = async (e: any) => {
    e.preventDefault();

    const params = {
        warehouse: searchByWarehouseForm.warehouse
    };

    const response = await fetch("/api/xml/filter-by-warehouse", {
        method: "POST",
        body: JSON.stringify(params),
        headers: {
            'content-type': 'application/json'
        }
    });

    if(!response.ok){
        toast.error(response.statusText);
        return;
    }

    const text = await response.text();
    const formattedXml = xmlFormatter(text);

    setXmlFilteredByWarehouse(formattedXml);
  };

  const handleSubmitPayment = async (e: any) => {
    e.preventDefault();

    const params = {
        payment: searchByPaymentForm.payment
    };

    const response = await fetch("/api/xml/filter-by-payment", {
        method: "POST",
        body: JSON.stringify(params),
        headers: {
            'content-type': 'application/json'
        }
    });

    if(!response.ok){
        toast.error(response.statusText);
        return;
    }

    const text = await response.text();
    const formattedXml = xmlFormatter(text);

    setXmlFilteredByPayment(formattedXml);
  };

  const handleSubmitProductLine = async (e: any) => {
    e.preventDefault();

    const params = {
        product_line: searchByProductLineForm.product_line
    };

    const response = await fetch("/api/xml/filter-by-product-line", {
        method: "POST",
        body: JSON.stringify(params),
        headers: {
            'content-type': 'application/json'
        }
    });

    if(!response.ok){
        toast.error(response.statusText);
        return;
    }

    const text = await response.text();
    const formattedXml = xmlFormatter(text);

    setXmlFilteredByProductLine(formattedXml);
  };

  return (
    <React.Fragment>
        <ToastContainer />

        <Dialog
          open={open}
          onClose={handleClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
          maxWidth="md"
          sx={{ '& .MuiDialog-paper': { minHeight: '80vh' } }}
        >
        <DialogTitle id="alert-dialog-title">
          {"XML Viewer"}
        </DialogTitle>

        <DialogContent>

            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                    <Tab label="Search by warehouse" {...a11yProps(0)} />
                    <Tab label="Search by payment method" {...a11yProps(1)} />
                    <Tab label="Search by product line" {...a11yProps(2)} />
                </Tabs>
            </Box>
            
            <CustomTabPanel value={value} index={0}>
                <Box className='px-0' component="form" onSubmit={handleSubmitWarehouse}>
                    <TextField
                        label="Search by warehouse name"
                        fullWidth
                        margin="normal"
                        value={searchByWarehouseForm.warehouse}
                        onChange={(e: any) => {setSearchByWarehouseForm({...searchByWarehouseForm, warehouse: e.target.value})}}
                    />

                    <Button fullWidth type="submit" variant="contained" startIcon={<Search />} />
                </Box>

                <pre className='my-4 mx-0' style={{ fontFamily: "monospace" }}>
                    <code>{xml_filtered_by_warehouse}</code>
                </pre>
            </CustomTabPanel>

            <CustomTabPanel value={value} index={1}>
                <Box className='px-0' component="form" onSubmit={handleSubmitPayment}>
                    <TextField
                        label="Search by payment method"
                        fullWidth
                        margin="normal"
                        value={searchByPaymentForm.payment}
                        onChange={(e: any) => {setSearchByPaymentForm({...searchByPaymentForm, payment: e.target.value})}}
                    />

                    <Button fullWidth type="submit" variant="contained" startIcon={<Search />} />
                </Box>

                <pre className='my-4 mx-0' style={{ fontFamily: "monospace" }}>
                    <code>{xml_filtered_by_payment}</code>
                </pre>
            </CustomTabPanel>

            <CustomTabPanel value={value} index={2}>
                <Box className='px-0' component="form" onSubmit={handleSubmitProductLine}>
                    <TextField
                        label="Search by product line"
                        fullWidth
                        margin="normal"
                        value={searchByProductLineForm.product_line}
                        onChange={(e: any) => {setSearchByProductLineForm({...searchByProductLineForm, product_line: e.target.value})}}
                    />

                    <Button fullWidth type="submit" variant="contained" startIcon={<Search />} />
                </Box>

                <pre className='my-4 mx-0' style={{ fontFamily: "monospace" }}>
                    <code>{xml_filtered_by_product_line}</code>
                </pre>
            </CustomTabPanel>
            
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
})

export default XmlViewerDialog