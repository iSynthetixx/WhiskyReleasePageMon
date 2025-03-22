from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional


class ItemModel(BaseModel):
    # Discard fields not explicitly defined in the model
    model_config = {"extra": "ignore"}
    id: str
    brand: str
    active: bool
    sourceImageURLs: List[str]
    displayName: str
    primaryFullImageURL: str
    b2c_highlyAllocatedProduct: str
    b2c_inventoryAvailability: Optional[str]
    x_volume: str
    listPrice: float
    onlineOnly: bool
    creationDate: str
    b2c_onlineAvailable: str
    b2c_onlineExclusive: str
    lastModifiedDate: str
    b2c_size: str
    b2c_proof: str
    b2c_futuresProduct: str
    b2c_comingSoon: str
    repositoryId: str
    b2c_type: str
    # primarySourceImageURL: str
    # b2c_productIdNumber: str
    # stockStatus: Optional[str] = None
    # productSkuInventoryStatus: Optional[dict] = None
    # locationId: Optional[str] = None
    # productSkuInventoryDetails: Optional[list] = None
    # catalogId: Optional[str] = None
    # productId: Optional[str] = None
    # preOrderableQuantity: Optional[int] = None
    # orderableQuantity: Optional[int] = None
    # availabilityDate: Optional[str] = None
    # backOrderableQuantity: Optional[int] = None
    # catRefId: Optional[str] = None
    # inStockQuantity: Optional[int] = None
    # Commented-out attributes
    # parentCategories: List[ParentCategory]
    # height: Optional[str]
    # defaultProductListingSku: Optional[str]
    # assetable: bool
    # unitOfMeasure: Optional[str]
    # targetAddOnProducts: List
    # b2c_glutenFree: str
    # b2c_disableBopis: str
    # b2c_chairmansSelection: str
    # seoUrlSlugDerived: str
    # b2c_region: Optional[str]
    # b2c_upc: str
    # x_salesTaxIndicator: str
    # thumbImageURLs: List[str]
    # b2c_paResidencyOnly: str
    # b2c_offerId: Optional[str]
    # b2c_tastingNotes: Optional[str]
    # b2c_chairmansSpirits: str
    # relatedArticles: List
    # mediumImageURLs: List[str]
    # primaryThumbImageURL: str
    # directCatalogs: List
    # nonreturnable: bool
    # b2c_taste: Optional[str]
    # b2c_mostPopular: Optional[str]
    # x_freightCost: Optional[str]
    # productVariantOptions: List[dict]
    # b2c_expertReviews: Optional[str]
    # primaryLargeImageURL: str
    # b2c_varietal: Optional[str]
    # saleVolumePrices: List
    # childSKUs: List[dict]
    # b2c_customerRatingsFilterSplit: Optional[str]
    # salePrice: Optional[str]
    # b2c_sortWeighting: Optional[str]
    # b2c_scotchType: Optional[str]
    # b2c_tastingNotesOakInfluence: Optional[str]
    # b2c_tastingNotesSweetness: Optional[str]
    # x_deliveryFee: Optional[str]
    # notForIndividualSale: bool
    # width: Optional[str]
    # b2c_expertRatingsFilter: Optional[str]
    # derivedListPriceFrom: str
    # defaultParentCategory: Optional[str]
    # b2c_regionFilterSplit: Optional[str]
    # b2c_quotedAtPrice: Optional[str]
    # x_alcoholicOrNonalcoholic: str
    # listVolumePrice: Optional[str]
    # b2c_featuredFilterSplit: str
    # excludeFromSitemap: bool
    # relatedProducts: Optional[str]
    # largeImageURLs: List[str]
    # listVolumePrices: List
    # addOnProducts: List
    # derivedSalePriceFrom: str
    # b2c_new: Optional[str]
    # b2c_topCustomerReviews: Optional[str]
    # primaryMediumImageURL: str
    # weight: Optional[str]
    # parentCategory: ParentCategory
    # primarySmallImageURL: str
    # b2c_salePriceType: Optional[str]
    # b2c_limitPerOrder: Optional[str]
    # avgCustRating: Optional[str]
    # b2c_featured: Optional[str]
    # longDescription: Optional[str]
    # b2c_vintage: Optional[str]
    # b2c_expertRatingsFilterSplitSort: Optional[str]
    # description: Optional[str]
    # salePrices: List
    # smallImageURLs: List[str]
    # b2b_hasCase: Optional[str]
    # derivedShippingSurchargeFrom: str
    # shippingSurcharges: List
    # b2c_organic: str
    # saleVolumePrice: Optional[str]
    # primaryImageTitle: str
    # b2c_expertRatingsFilterSplit: Optional[str]
    # relatedMediaContent: List
    # length: Optional[str]
    # b2c_lotteryRegistrationDescription: Optional[str]
    # variantValuesOrder: dict
    # shippingSurcharge: Optional[str]
    # productImagesMetadata: List[dict]
    # derivedDirectCatalogs: List
    # configurable: bool
    # class Config:
        # extra = "allow"


class ResponseModel(BaseModel):
    totalResults: int
    # offset: int
    # limit: int
    # links: List[Link]
    # category: Category
    items: List[Item]
    class Config:
        extra = "allow"

class StockItemModel(BaseModel):
    # Discard fields not explicitly defined in the model
    model_config = {"extra": "ignore"}
    stockStatus: Optional[str] = None
    productSkuInventoryStatus: Optional[dict] = None
    locationId: Optional[str] = None
    productSkuInventoryDetails: Optional[list] = None
    catalogId: Optional[str] = None
    productId: Optional[str] = None
    preOrderableQuantity: Optional[int] = None
    locationId: Optional[str] = None
    orderableQuantity: Optional[int] = None
    stockStatus: Optional[str] = None
    availabilityDate: Optional[str] = None
    backOrderableQuantity: Optional[int] = None
    catRefId: Optional[str] = None
    inStockQuantity: Optional[int] = None
    id: Optional[str] = None

    # class Config:
        # extra = "allow"

