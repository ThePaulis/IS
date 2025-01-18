import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
    const warehouseName = req.nextUrl.searchParams.get('warehouseName');

    const headers = {
        'content-type': 'application/json',
    };

    const options = {
        method: 'GET',
        headers,
    };

    try {   
        if(!warehouseName) {
            return NextResponse.json({ status: 400, message: 'Missing warehouse name' }, { status: 400 });
        }
        console.log('Fetching sales data for warehouse:', warehouseName);
        const response = await fetch(`${process.env.REST_API_BASE_URL}/api/sales/warehouse/?warehouse=${encodeURIComponent(warehouseName)}`, options);

        if (!response.ok) {
            const errorResponse = await response.text();
            console.log('Response status:', response.status);
            console.log('Response status text:', response.statusText);
            console.log('Response body:', errorResponse);
            return NextResponse.json({ status: response.status, message: response.statusText }, { status: response.status });
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (e) {
        console.log(e);
        return NextResponse.json({ status: 500, message: e }, { status: 500 });
    }
}