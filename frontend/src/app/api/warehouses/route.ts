import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const request_body  = await req.json()

    const warehouse = request_body?.search ?? ''

    const headers = {
        'content-type': 'application/json',
    }
    
    const query = `query Warehouses{allWarehouses${warehouse.length > 0 ? `(name: "${warehouse}")` : ''}{
            id
            name
            latitude
            longitude
        }
    }`;

    // Use the service name for the URL
    const url = `${process.env.GRAPHQL_API_BASE_URL}/graphql/?query=${encodeURIComponent(query)}`;

    const options = {
        method: 'POST',
        headers,
        body: JSON.stringify({ query })
    };

    console.log('URL:', url);
    console.log('Options:', options);

    try {
        const promise = await fetch(url, options)
        if (!promise.ok) {
            const errorResponse = await promise.text();
            console.log('Response status:', promise.status);
            console.log('Response status text:', promise.statusText);
            console.log('Response body:', errorResponse);
            return NextResponse.json({status: promise.status, message: promise.statusText, body: errorResponse}, { status: promise.status }) 
        }
        const data = await promise.json()
        console.log(data)

        return NextResponse.json(data) 
    } catch (e) {
        console.log(e)
        return NextResponse.json({status: 500, message: e}, { status: 500 }) 
    }
}