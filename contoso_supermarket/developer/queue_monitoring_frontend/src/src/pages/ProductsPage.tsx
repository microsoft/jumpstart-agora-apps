import React, { useCallback, useEffect } from "react";
import { Product, useGlobalContext } from "../providers/GlobalContext";
import Header from "../components/header/Header";
import { IconTrash } from "../images";
import ModalConfirmation from "../components/modal/ModalConfirmation";

function ProductsPage() {
    const { getProducts, products, updateProducts, deleteProduct } = useGlobalContext();
    const [productList, setProductList] = React.useState<Product[]>([]);
    const [openSaveModal, setOpenSaveModal] = React.useState(false);
    const [openDeleteModal, setOpenDeleteModal] = React.useState(false);
    const [deletedProductId, setDeletedProductId] = React.useState<number | undefined>();

    //initial data load
    useEffect(() => {
        getProducts && getProducts();
    }, [getProducts]);

    //sets our product list
    useEffect(() => {
        setProductList(products);
    }, [products]);

    const updateProduct = (productId: number, key: string, value: string | number | null) => {
        setProductList((x) => x.map((item) => (item.id === productId ? { ...item, [key]: value } : item)));
    };

    const onSaveProducts = () => {
        if (updateProducts) {
            updateProducts(productList);
        }
    };

    const onDeleteProduct = useCallback(() => {
        if (deleteProduct && deletedProductId) {
            deleteProduct(deletedProductId);
        }
    }, [deletedProductId, deleteProduct]);

    return (
        <>
            <Header />
            <ModalConfirmation
                open={openSaveModal}
                onCancelButtonClick={() => setOpenSaveModal(false)}
                onActionButtonClick={() => onSaveProducts()}
                setOpen={setOpenSaveModal}
                actionButtonClass="btn-primary"
                actionButtonText="Save"
                cancelButtonText="Cancel"
                title="Confirmation"
                body="Are you sure you want to Save Changes?"
            />
            <ModalConfirmation
                open={openDeleteModal}
                onCancelButtonClick={() => setOpenDeleteModal(false)}
                onActionButtonClick={() => onDeleteProduct()}
                setOpen={setOpenDeleteModal}
                actionButtonClass="btn-danger"
                actionButtonText="Delete"
                cancelButtonText="Cancel"
                title="Confirmation"
                body="Are you sure you want to delete this product?"
            />
            <div className="flex flex-col py-4 px-8 px-sm-8 container">
                <h1 className="text-primary mb-2 fs-2">Product List</h1>
                <table className="table">
                    <thead>
                        <tr>
                            <th scope="col" className="col-1 text-center">
                                ID
                            </th>
                            <th scope="col" className="col-4 text-center">
                                Name
                            </th>
                            <th scope="col" className="col-4 text-center">
                                Description
                            </th>
                            <th scope="col" className="col-2 text-center">
                                Unit Price
                            </th>
                            <th scope="col" className="col-1 text-center">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="table-group-divider">
                        {productList.map((item: Product) => {
                            return (
                                <tr key={item.id} className="border-grey border-2 fs-5">
                                    <td className="col-1 text-center">{item.id}</td>
                                    <td className="col-4 text-center">
                                        <div className="input-group flex-nowrap">
                                            <input
                                                className="form-control"
                                                type="text"
                                                value={item.name}
                                                onChange={(e) => updateProduct(item.id, "name", e.currentTarget.value)}
                                            />
                                        </div>
                                    </td>
                                    <td className="col-4 text-center">
                                        <div className="input-group flex-nowrap">
                                            <textarea
                                                className="form-control"
                                                rows={1}
                                                value={item.description}
                                                onChange={(e) =>
                                                    updateProduct(item.id, "description", e.currentTarget.value)
                                                }
                                            />
                                        </div>
                                    </td>
                                    <td className="col-2 text-center">
                                        <div className="d-flex">
                                            <div className="input-group flex-nowrap">
                                                <span className="input-group-text" id="addon-wrapping">
                                                    $
                                                </span>
                                                <input
                                                    className="form-control"
                                                    type="number"
                                                    step={0.01}
                                                    value={item.price}
                                                    onChange={(e) =>
                                                        updateProduct(item.id, "price", e.currentTarget.value)
                                                    }
                                                />
                                            </div>
                                        </div>
                                    </td>
                                    <td className="col-1 text-center">
                                        <button
                                            className="btn-delete-product border-0 bg-transparent"
                                            onClick={() => {
                                                setDeletedProductId(item.id);
                                                setOpenDeleteModal(true);
                                            }}
                                        >
                                            <IconTrash />
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
                <div className="d-flex">
                    <button
                        id="btn-save-products"
                        className="btn bg-primary text-white px-5 shadow ms-auto"
                        onClick={() => setOpenSaveModal(true)}
                    >
                        Save Changes
                    </button>
                </div>
            </div>
        </>
    );
}

export default ProductsPage;
