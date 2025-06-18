import pandas as pd
from app import app, db
from models import Product
from sqlalchemy.exc import SQLAlchemyError

def import_from_csv(filename):
    try:
        df = pd.read_csv(filename, encoding='utf-8-sig')

        # Pastikan kolom yang dibutuhkan tersedia
        required_columns = {
            'product_name', 'product_price', 'original_price', 'saved_amount',
            'source_website', 'brand', 'image_url', 'rating',
            'description', 'how_to_use', 'ingredients'
        }

        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            print(f"❌ Kolom yang hilang di CSV: {missing}")
            return

        with app.app_context():
            imported_count = 0
            for _, row in df.iterrows():
                try:
                    rating_value = None
                    if pd.notna(row.get('rating')):
                        try:
                            rating_value = float(row.get('rating'))
                        except ValueError:
                            rating_value = None

                    product = Product(
                        product_name=row.get('product_name'),
                        product_price=row.get('product_price'),
                        original_price=row.get('original_price'),
                        saved_amount=row.get('saved_amount'),
                        source_website=row.get('source_website'),
                        brand=row.get('brand'),
                        image_url=row.get('image_url'),
                        rating=rating_value,
                        description=row.get('description'),
                        usage_instructions=row.get('how_to_use'),
                        ingredients=row.get('ingredients')
                    )
                    db.session.add(product)
                    imported_count += 1
                except Exception as item_error:
                    print(f"⚠️ Gagal impor baris: {row.to_dict()}")
                    print(f"    Error: {item_error}")

            db.session.commit()
            print(f"✅ Import selesai. Total produk berhasil diimpor: {imported_count}")
    except FileNotFoundError:
        print(f"❌ File tidak ditemukan: {filename}")
    except pd.errors.ParserError as e:
        print(f"❌ Gagal membaca CSV: {e}")
    except SQLAlchemyError as db_err:
        print(f"❌ Error database: {db_err}")
        db.session.rollback()
    except Exception as e:
        print(f"❌ Terjadi error tak terduga: {e}")

if __name__ == '__main__':
    import_from_csv('scraped_data/sociolla_all_products.csv')
