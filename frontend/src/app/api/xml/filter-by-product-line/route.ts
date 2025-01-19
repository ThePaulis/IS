import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const request_body  = await req.json()

    const product_line= request_body?.product_line ?? ''


    const requestOptions = {
        method: "POST",
        body: JSON.stringify({
            "product_line":  `${product_line}`
        }),
        headers: {
            'content-type': 'application/json'
        }
    }

    try{
        const promise = await fetch(`${process.env.REST_API_BASE_URL}/api/subxml-product-line/`, requestOptions)

        if(!promise.ok){
            const errorResponse = await promise.text();
            console.log('Response status:', promise.status);
            console.log('Response status text:', promise.statusText);
            console.log('Response body:', errorResponse);
            return NextResponse.json({status: promise.status, message: promise.statusText}, { status: promise.status }) 
        }

        const jsonResponse = await promise.json();
        const subxmlContent = jsonResponse.subxml_content;
        const wrappedSubxmlContent = `<Sales>${subxmlContent}</Sales>`;
        return new Response(wrappedSubxmlContent, { headers: { "Content-Type": "text/xml" } });
    }catch(e){
        console.log(e)

        return NextResponse.json({status: 500, message: e}, { status: 500  }) 
    }
}
