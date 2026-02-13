export type Beverage = {
  id: string;
  barcode?: string | null;
  brand?: string | null;
  product_name?: string | null;
  category?: string | null;
  abv_percent?: number | null;
  volume_ml?: number | null;
  source?: string | null;
  created_at?: string;
};

export type DrinkEntry = {
  id: string;
  user_id: string;
  beverage_id?: string | null;
  quantity: number;
  abv_percent?: number | null;
  volume_ml?: number | null;
  consumed_at?: string;
  pure_alcohol_ml?: number | null;
  created_at?: string;
};

export type RecognitionResult = {
  brand?: string | null;
  productName?: string | null;
  category?: string | null;
  abvPercent?: number | null;
  volumeMl?: number | null;
  quantity?: number | null;
  confidence?: number | null;
  rawOcr?: string[] | null;
};

export type StatPoint = {
  label: string;
  value: number;
};
