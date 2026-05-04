from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.payments.confirm_payment import ConfirmPaymentUseCase
from src.application.payments.create_payment_intent import CreatePaymentIntentUseCase
from src.application.payments.refund_payment import RefundPaymentUseCase
from src.core.exceptions import EntityNotFound, PaymentFailed
from src.presentation.api.deps import (
    CurrentUser,
    ManagerOrAbove,
    get_cache_service,
    get_email_service,
    get_order_repo,
    get_payment_repo,
    get_payment_service,
    get_product_repo,
    get_user_repo,
)
from src.presentation.schemas.payment import (
    ConfirmPaymentRequest,
    PaymentIntentResponse,
    PaymentResponse,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/intent", response_model=PaymentIntentResponse, status_code=201)
async def create_payment_intent(
    order_id: UUID,
    current_user: CurrentUser,
    order_repo=Depends(get_order_repo),
    payment_repo=Depends(get_payment_repo),
    payment_service=Depends(get_payment_service),
):
    try:
        use_case = CreatePaymentIntentUseCase(order_repo, payment_repo, payment_service)
        result = await use_case.execute(order_id, current_user.id)
        return PaymentIntentResponse(
            payment_id=result.payment_id,
            payment_intent_id=result.payment_intent_id,
            client_secret=result.client_secret,
            amount=result.amount,
            currency=result.currency,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/confirm", response_model=PaymentResponse)
async def confirm_payment(
    body: ConfirmPaymentRequest,
    current_user: CurrentUser,
    payment_repo=Depends(get_payment_repo),
    order_repo=Depends(get_order_repo),
    product_repo=Depends(get_product_repo),
    user_repo=Depends(get_user_repo),
    payment_service=Depends(get_payment_service),
    email_service=Depends(get_email_service),
    cache=Depends(get_cache_service),
):
    try:
        use_case = ConfirmPaymentUseCase(
            payment_repo, order_repo, product_repo, user_repo,
            payment_service, email_service, cache,
        )
        payment = await use_case.execute(body.payment_intent_id, body.payment_method)
        return PaymentResponse(
            id=payment.id,
            order_id=payment.order_id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            payment_intent_id=payment.payment_intent_id,
            payment_method=payment.payment_method,
            created_at=payment.created_at,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PaymentFailed as e:
        raise HTTPException(status_code=402, detail=str(e))


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: UUID,
    _: ManagerOrAbove,
    payment_repo=Depends(get_payment_repo),
    order_repo=Depends(get_order_repo),
    payment_service=Depends(get_payment_service),
):
    try:
        use_case = RefundPaymentUseCase(payment_repo, order_repo, payment_service)
        payment = await use_case.execute(payment_id)
        return PaymentResponse(
            id=payment.id,
            order_id=payment.order_id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            payment_intent_id=payment.payment_intent_id,
            payment_method=payment.payment_method,
            created_at=payment.created_at,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
