import { api } from '../../api/client'
import { useApi } from '../../hooks/useApi'
import {
  formatCompactCurrency,
  formatCurrency,
  formatNumber,
} from '../../utils/format'
import { categoryItems } from '../../utils/transform'
import { AsyncContent, EmptyState } from '../AsyncContent'
import { BarList } from '../BarList'
import { Section } from '../Section'
import { StatGrid, StatTile } from '../StatTile'

export function ProductsSection() {
  const result = useApi(api.getProducts)

  return (
    <Section
      id="products"
      title="Products and categories"
      description="Catalog size and the best-selling categories by product revenue."
    >
      <AsyncContent result={result} lines={8}>
        {(data) => (
          <div className="stack">
            <StatGrid label="Product metrics">
              <StatTile
                label="Products in catalog"
                value={formatNumber(data.total_products)}
              />
              <StatTile
                label="Missing a category"
                value={formatNumber(data.products_missing_category)}
                note="Shown as “unknown”"
              />
            </StatGrid>

            <div>
              <h3 className="subheading">
                Top {data.top_categories.length} categories by revenue
              </h3>
              {data.top_categories.length === 0 ? (
                <EmptyState>No product sales were found.</EmptyState>
              ) : (
                <BarList
                  items={categoryItems(data.top_categories)}
                  label="Top categories by product revenue"
                  formatValue={formatCompactCurrency}
                  formatDetail={(quantity) => `${formatNumber(quantity)} items sold`}
                />
              )}
            </div>

            {data.top_products.length > 0 && (
              <details className="details">
                <summary>Top {data.top_products.length} products by items sold</summary>
                <div className="table-scroll" tabIndex={0} aria-label="Top products table">
                  <table className="table table--compact">
                    <thead>
                      <tr>
                        <th scope="col">Product ID</th>
                        <th scope="col" className="numeric">
                          Items sold
                        </th>
                        <th scope="col" className="numeric">
                          Revenue
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.top_products.map((product) => (
                        <tr key={product.product_id}>
                          <td>
                            <code className="id">{product.product_id}</code>
                          </td>
                          <td className="numeric">
                            {formatNumber(product.quantity_sold)}
                          </td>
                          <td className="numeric">{formatCurrency(product.revenue)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </details>
            )}
          </div>
        )}
      </AsyncContent>
    </Section>
  )
}
