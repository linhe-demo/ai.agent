# app/models/invoice.py
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class InvoiceMetadata(BaseModel):
    """发票元数据"""
    filename: str
    file_type: str
    index: int
    ocr_text_preview: Optional[str] = None
    pre_classified_type: Optional[str] = None
    processing_time: Optional[float] = None


class InvoiceData(BaseModel):
    """发票数据"""
    invoice_type: Optional[str] = Field(None, description="发票类型")
    invoice_code: Optional[str] = Field(None, description="发票代码")
    invoice_number: Optional[str] = Field(None, description="发票号码")
    invoice_date: Optional[str] = Field(None, description="开票日期")
    buyer_name: Optional[str] = Field(None, description="购买方名称")
    buyer_tax_id: Optional[str] = Field(None, description="购买方纳税人识别号")
    buyer_address_phone: Optional[str] = Field(None, description="购买方地址电话")
    buyer_bank_account: Optional[str] = Field(None, description="购买方开户行及账号")
    seller_name: Optional[str] = Field(None, description="销售方名称")
    seller_tax_id: Optional[str] = Field(None, description="销售方纳税人识别号")
    seller_address_phone: Optional[str] = Field(None, description="销售方地址电话")
    seller_bank_account: Optional[str] = Field(None, description="销售方开户行及账号")
    total_amount: Optional[float] = Field(None, description="总金额（不含税）")
    tax_rate: Optional[str] = Field(None, description="税率")
    tax_amount: Optional[float] = Field(None, description="税额")
    total_amount_with_tax: Optional[float] = Field(None, description="价税合计")
    goods_name: Optional[str] = Field(None, description="货物或应税劳务名称")
    metadata: Optional[InvoiceMetadata] = Field(None, description="元数据")  # 改名：去掉下划线


class InvoiceClassification(BaseModel):
    """发票分类信息"""
    type: str
    is_special: bool
    is_normal: bool
    description: str


class InvoiceResult(BaseModel):
    """单张发票处理结果"""
    index: int
    filename: str
    status: str  # success / failed
    data: Optional[InvoiceData] = None
    error: Optional[str] = None


class InvoiceSummary(BaseModel):
    """发票识别汇总"""
    total: int
    success: int
    failed: int
    special_invoice_count: int = 0
    normal_invoice_count: int = 0
    unknown_invoice_count: int = 0


class BatchInvoiceResponse(BaseModel):
    """批量发票识别响应"""
    code: int = 0
    message: str
    summary: InvoiceSummary
    results: List[InvoiceResult]