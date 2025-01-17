import { NextRequest, NextResponse } from 'next/server'
 
export async function PUT(req: NextRequest) {
    const request_body  = await req.json()
    const id            = req.nextUrl.pathname.split("/")[3]

    const headers = {
        'content-type': 'application/json',
    }
    
    const graphqlQuery = {
        query: `
            mutation UpdateWarehouse($id: ID!, $latitude: String!, $longitude: String!) {
                updateWarehouse(id: $id, latitude: $latitude, longitude: $longitude) {
                    warehouse {
                        id
                        latitude
                        longitude
                        name
                    }
                }
            }
        `,
        variables: {
            id: id,
            latitude: request_body.latitude.toString(),
            longitude: request_body.longitude.toString()
        }
    }

    console.log('Query:', graphqlQuery)
    
    const options = {
        method: 'POST',
        headers,
        body: JSON.stringify(graphqlQuery)
    }

    try{
        const promise = await fetch(`${process.env.GRAPHQL_API_BASE_URL}/graphql/`, options)

        if(!promise.ok){
            const errorResponse = await promise.text();
            console.log('Response status:', promise.status);
            console.log('Response status text:', promise.statusText);
            console.log('Response body:', errorResponse);
            return NextResponse.json({status: promise.status, message: promise.statusText}, { status: promise.status }) 
        }

        const data = await promise.json()

        return NextResponse.json(data) 
    }catch(e){
        console.log(e)
        return NextResponse.json({status: 500, message: e}, { status: 500  }) 
    }
}
