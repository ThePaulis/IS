export interface Warehouse{
    id: string
    name: string
    latitude: number
    longitude: number
}

export interface Warehouses{
    allWarehouses: Warehouse[]
}

export interface GraphQlWarehouses{
    data: Warehouses
}