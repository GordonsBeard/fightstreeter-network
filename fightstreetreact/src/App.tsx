import { RouterProvider } from "react-router-dom";
import { router } from "./routes/router.tsx";
import Header from './components/ui/Header.tsx';
import 'bootstrap/dist/css/bootstrap.css';
import { Suspense } from "react";

export default function App() {
    return (
        <>
            <Header />
            <div className="container-fluid">
                <main className="col-md-12">
                    <Suspense fallback={<div className="container">Loading...</div>}>
                        <RouterProvider router={router} />
                    </Suspense>
                </main>
            </div>
        </>
    );
}