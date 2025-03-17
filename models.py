from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional


class ItemModel(BaseModel):
    # b2c_expertRatings: Optional[str]
    # b2c_age: Optional[str]
    # orderLimit: Optional[str]
    # listPrices: ListPrices
    # x_volumeUOM: Optional[str]
    # type: str
    # b2c_tastingNotesBody: Optional[str]
    # gc_description: Optional[str]
    # b2c_lotteryPackageDescription: Optional[str]
    shippable: bool
    # b2c_size_sort: str
    primaryImageAltText: str
    id: str
    brand: str
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
    active: bool
    b2c_upc: str
    # x_salesTaxIndicator: str
    # thumbImageURLs: List[str]
    b2c_type: str
    # b2c_paResidencyOnly: str
    # b2c_offerId: Optional[str]
    b2c_tastingNotes: Optional[str]
    # b2c_chairmansSpirits: str
    route: str
    x_volumeOZ: str
    # relatedArticles: List
    b2c_productIdNumber: str
    # mediumImageURLs: List[str]
    primarySourceImageURL: str
    sourceImageURLs: List[str]
    minOrderLimit: Optional[str]
    # primaryThumbImageURL: str
    # directCatalogs: List
    # nonreturnable: bool
    displayName: str
    # b2c_taste: Optional[str]
    # b2c_mostPopular: Optional[str]
    primaryFullImageURL: str
    # x_freightCost: Optional[str]
    # productVariantOptions: List[dict]
    # b2c_expertReviews: Optional[str]
    # primaryLargeImageURL: str
    b2c_highlyAllocatedProduct: str
    b2c_inventoryAvailability: Optional[str]
    # b2c_varietal: Optional[str]
    # saleVolumePrices: List
    # childSKUs: List[dict]
    # b2c_customerRatingsFilterSplit: Optional[str]
    # salePrice: Optional[str]
    x_volume: str
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
    listPrice: float
    # b2c_quotedAtPrice: Optional[str]
    # x_alcoholicOrNonalcoholic: str
    # listVolumePrice: Optional[str]
    # b2c_featuredFilterSplit: str
    # excludeFromSitemap: bool
    b2c_freightIncludedSalePrice: float
    # relatedProducts: Optional[str]
    onlineOnly: bool
    # largeImageURLs: List[str]
    b2c_freightIncludedListPrice: float
    # listVolumePrices: List
    # addOnProducts: List
    # derivedSalePriceFrom: str
    x_type: str
    # b2c_new: Optional[str]
    # b2c_topCustomerReviews: Optional[str]
    # primaryMediumImageURL: str
    b2c_country: str
    # weight: Optional[str]
    creationDate: str
    parentCategoryIdPath: str
    x_typeDisplay: str
    # parentCategory: ParentCategory
    # primarySmallImageURL: str
    # b2c_salePriceType: Optional[str]
    # b2c_limitPerOrder: Optional[str]
    # avgCustRating: Optional[str]
    # b2c_featured: Optional[str]
    # longDescription: Optional[str]
    # b2c_vintage: Optional[str]
    b2c_onlineAvailable: str
    # b2c_expertRatingsFilterSplitSort: Optional[str]
    # description: Optional[str]
    # salePrices: List
    b2c_onlineExclusive: str
    b2c_specialOrderAddressShip: str
    b2c_freightIncludedActivePrice: float
    b2c_lotteryProduct: str
    b2c_lotteryAvailabilityDescription: Optional[str]
    # smallImageURLs: List[str]
    # b2b_hasCase: Optional[str]
    # derivedShippingSurchargeFrom: str
    # shippingSurcharges: List
    # b2c_organic: str
    # saleVolumePrice: Optional[str]
    primaryImageTitle: str
    # b2c_expertRatingsFilterSplit: Optional[str]
    b2c_specialOrderProduct: str
    b2c_clearance: str
    # relatedMediaContent: List
    lastModifiedDate: str
    fullImageURLs: List[str]
    b2c_size: str
    # length: Optional[str]
    b2c_proof: str
    # derivedDirectCatalogs: List
    b2c_futuresProduct: str
    # b2c_lotteryRegistrationDescription: Optional[str]
    b2c_comingSoon: str
    # variantValuesOrder: dict
    repositoryId: str
    # shippingSurcharge: Optional[str]
    # productImagesMetadata: List[dict]
    b2c_madeInPa: str
    # configurable: bool
    class Config:
        extra = "allow"


class ResponseModel(BaseModel):
    totalResults: int
    # offset: int
    # limit: int
    # links: List[Link]
    # category: Category
    items: List[Item]
    class Config:
        extra = "allow"
