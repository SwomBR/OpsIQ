import { Header } from './components/Header'
import { CustomersSection } from './components/sections/CustomersSection'
import { DeliverySection } from './components/sections/DeliverySection'
import { ExceptionsSection } from './components/sections/ExceptionsSection'
import { OrderStatusSection } from './components/sections/OrderStatusSection'
import { ProductsSection } from './components/sections/ProductsSection'
import { SalesSection } from './components/sections/SalesSection'
import { SummarySection } from './components/sections/SummarySection'

export default function App() {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to dashboard
      </a>
      <Header />
      <main id="main" className="dashboard">
        <SummarySection />
        <DeliverySection />
        <OrderStatusSection />
        <ExceptionsSection />
        <SalesSection />
        <ProductsSection />
        <CustomersSection />
      </main>
      <footer className="app-footer">
        <p>
          Data: Olist Brazilian E-Commerce Public Dataset (Kaggle), licensed
          CC BY-NC-SA 4.0. All figures are calculated from the dataset by the
          OpsIQ API; money is in Brazilian reais (BRL).
        </p>
      </footer>
    </>
  )
}
