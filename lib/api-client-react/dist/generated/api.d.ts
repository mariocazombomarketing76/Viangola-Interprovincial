import type { QueryKey, UseMutationOptions, UseMutationResult, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import type { Booking, BookingInput, Dashboard, HealthStatus, ListBookingsParams, ListTripsParams, Payment, Trip, TripInput, TripSeat } from './api.schemas';
import { customFetch } from '../custom-fetch';
import type { ErrorType, BodyType } from '../custom-fetch';
type AwaitedInput<T> = PromiseLike<T> | T;
type Awaited<O> = O extends AwaitedInput<infer T> ? T : never;
type SecondParameter<T extends (...args: never) => unknown> = Parameters<T>[1];
export declare const getHealthCheckUrl: () => string;
/**
 * @summary Health check
 */
export declare const healthCheck: (options?: Parameters<typeof customFetch>[1]) => Promise<HealthStatus>;
export declare const getHealthCheckQueryKey: () => readonly ["/api/healthz"];
export declare const getHealthCheckQueryOptions: <TData = Awaited<ReturnType<typeof healthCheck>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData> & {
    queryKey: QueryKey;
};
export type HealthCheckQueryResult = NonNullable<Awaited<ReturnType<typeof healthCheck>>>;
export type HealthCheckQueryError = ErrorType<unknown>;
/**
 * @summary Health check
 */
export declare function useHealthCheck<TData = Awaited<ReturnType<typeof healthCheck>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getGetDashboardUrl: () => string;
/**
 * @summary Obter resumo operacional
 */
export declare const getDashboard: (options?: Parameters<typeof customFetch>[1]) => Promise<Dashboard>;
export declare const getGetDashboardQueryKey: () => readonly ["/api/dashboard"];
export declare const getGetDashboardQueryOptions: <TData = Awaited<ReturnType<typeof getDashboard>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getDashboard>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof getDashboard>>, TError, TData> & {
    queryKey: QueryKey;
};
export type GetDashboardQueryResult = NonNullable<Awaited<ReturnType<typeof getDashboard>>>;
export type GetDashboardQueryError = ErrorType<unknown>;
/**
 * @summary Obter resumo operacional
 */
export declare function useGetDashboard<TData = Awaited<ReturnType<typeof getDashboard>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getDashboard>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getListTripsUrl: (params?: ListTripsParams) => string;
/**
 * @summary Pesquisar viagens
 */
export declare const listTrips: (params?: ListTripsParams, options?: Parameters<typeof customFetch>[1]) => Promise<Trip[]>;
export declare const getListTripsQueryKey: (params?: ListTripsParams) => readonly ["/api/trips", ...ListTripsParams[]];
export declare const getListTripsQueryOptions: <TData = Awaited<ReturnType<typeof listTrips>>, TError = ErrorType<unknown>>(params?: ListTripsParams, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listTrips>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof listTrips>>, TError, TData> & {
    queryKey: QueryKey;
};
export type ListTripsQueryResult = NonNullable<Awaited<ReturnType<typeof listTrips>>>;
export type ListTripsQueryError = ErrorType<unknown>;
/**
 * @summary Pesquisar viagens
 */
export declare function useListTrips<TData = Awaited<ReturnType<typeof listTrips>>, TError = ErrorType<unknown>>(params?: ListTripsParams, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listTrips>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getCreateTripUrl: () => string;
/**
 * @summary Criar viagem
 */
export declare const createTrip: (tripInput: TripInput, options?: Parameters<typeof customFetch>[1]) => Promise<Trip>;
export declare const getCreateTripMutationOptions: <TError = ErrorType<unknown>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof createTrip>>, TError, {
        data: BodyType<TripInput>;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationOptions<Awaited<ReturnType<typeof createTrip>>, TError, {
    data: BodyType<TripInput>;
}, TContext>;
export type CreateTripMutationResult = NonNullable<Awaited<ReturnType<typeof createTrip>>>;
export type CreateTripMutationBody = BodyType<TripInput>;
export type CreateTripMutationError = ErrorType<unknown>;
/**
* @summary Criar viagem
*/
export declare const useCreateTrip: <TError = ErrorType<unknown>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof createTrip>>, TError, {
        data: BodyType<TripInput>;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationResult<Awaited<ReturnType<typeof createTrip>>, TError, {
    data: BodyType<TripInput>;
}, TContext>;
export declare const getGetTripUrl: (tripId: number) => string;
/**
 * @summary Obter viagem
 */
export declare const getTrip: (tripId: number, options?: Parameters<typeof customFetch>[1]) => Promise<Trip>;
export declare const getGetTripQueryKey: (tripId: number) => readonly [`/api/trips/${number}`];
export declare const getGetTripQueryOptions: <TData = Awaited<ReturnType<typeof getTrip>>, TError = ErrorType<void>>(tripId: number, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getTrip>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof getTrip>>, TError, TData> & {
    queryKey: QueryKey;
};
export type GetTripQueryResult = NonNullable<Awaited<ReturnType<typeof getTrip>>>;
export type GetTripQueryError = ErrorType<void>;
/**
 * @summary Obter viagem
 */
export declare function useGetTrip<TData = Awaited<ReturnType<typeof getTrip>>, TError = ErrorType<void>>(tripId: number, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getTrip>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getGetTripSeatsUrl: (tripId: number) => string;
/**
 * @summary Obter lugares da viagem
 */
export declare const getTripSeats: (tripId: number, options?: Parameters<typeof customFetch>[1]) => Promise<TripSeat[]>;
export declare const getGetTripSeatsQueryKey: (tripId: number) => readonly [`/api/trips/${number}/seats`];
export declare const getGetTripSeatsQueryOptions: <TData = Awaited<ReturnType<typeof getTripSeats>>, TError = ErrorType<unknown>>(tripId: number, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getTripSeats>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof getTripSeats>>, TError, TData> & {
    queryKey: QueryKey;
};
export type GetTripSeatsQueryResult = NonNullable<Awaited<ReturnType<typeof getTripSeats>>>;
export type GetTripSeatsQueryError = ErrorType<unknown>;
/**
 * @summary Obter lugares da viagem
 */
export declare function useGetTripSeats<TData = Awaited<ReturnType<typeof getTripSeats>>, TError = ErrorType<unknown>>(tripId: number, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getTripSeats>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getListBookingsUrl: (params?: ListBookingsParams) => string;
/**
 * @summary Listar reservas
 */
export declare const listBookings: (params?: ListBookingsParams, options?: Parameters<typeof customFetch>[1]) => Promise<Booking[]>;
export declare const getListBookingsQueryKey: (params?: ListBookingsParams) => readonly ["/api/bookings", ...ListBookingsParams[]];
export declare const getListBookingsQueryOptions: <TData = Awaited<ReturnType<typeof listBookings>>, TError = ErrorType<unknown>>(params?: ListBookingsParams, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listBookings>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof listBookings>>, TError, TData> & {
    queryKey: QueryKey;
};
export type ListBookingsQueryResult = NonNullable<Awaited<ReturnType<typeof listBookings>>>;
export type ListBookingsQueryError = ErrorType<unknown>;
/**
 * @summary Listar reservas
 */
export declare function useListBookings<TData = Awaited<ReturnType<typeof listBookings>>, TError = ErrorType<unknown>>(params?: ListBookingsParams, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listBookings>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getCreateBookingUrl: () => string;
/**
 * @summary Reservar lugar
 */
export declare const createBooking: (bookingInput: BookingInput, options?: Parameters<typeof customFetch>[1]) => Promise<Booking>;
export declare const getCreateBookingMutationOptions: <TError = ErrorType<unknown>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof createBooking>>, TError, {
        data: BodyType<BookingInput>;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationOptions<Awaited<ReturnType<typeof createBooking>>, TError, {
    data: BodyType<BookingInput>;
}, TContext>;
export type CreateBookingMutationResult = NonNullable<Awaited<ReturnType<typeof createBooking>>>;
export type CreateBookingMutationBody = BodyType<BookingInput>;
export type CreateBookingMutationError = ErrorType<unknown>;
/**
* @summary Reservar lugar
*/
export declare const useCreateBooking: <TError = ErrorType<unknown>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof createBooking>>, TError, {
        data: BodyType<BookingInput>;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationResult<Awaited<ReturnType<typeof createBooking>>, TError, {
    data: BodyType<BookingInput>;
}, TContext>;
export declare const getListPaymentsUrl: () => string;
/**
 * @summary Listar pagamentos
 */
export declare const listPayments: (options?: Parameters<typeof customFetch>[1]) => Promise<Payment[]>;
export declare const getListPaymentsQueryKey: () => readonly ["/api/payments"];
export declare const getListPaymentsQueryOptions: <TData = Awaited<ReturnType<typeof listPayments>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listPayments>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof listPayments>>, TError, TData> & {
    queryKey: QueryKey;
};
export type ListPaymentsQueryResult = NonNullable<Awaited<ReturnType<typeof listPayments>>>;
export type ListPaymentsQueryError = ErrorType<unknown>;
/**
 * @summary Listar pagamentos
 */
export declare function useListPayments<TData = Awaited<ReturnType<typeof listPayments>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listPayments>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getConfirmPaymentUrl: (paymentId: number) => string;
/**
 * @summary Confirmar pagamento
 */
export declare const confirmPayment: (paymentId: number, options?: Parameters<typeof customFetch>[1]) => Promise<Payment>;
export declare const getConfirmPaymentMutationOptions: <TError = ErrorType<unknown>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof confirmPayment>>, TError, {
        paymentId: number;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationOptions<Awaited<ReturnType<typeof confirmPayment>>, TError, {
    paymentId: number;
}, TContext>;
export type ConfirmPaymentMutationResult = NonNullable<Awaited<ReturnType<typeof confirmPayment>>>;
export type ConfirmPaymentMutationError = ErrorType<unknown>;
/**
* @summary Confirmar pagamento
*/
export declare const useConfirmPayment: <TError = ErrorType<unknown>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof confirmPayment>>, TError, {
        paymentId: number;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationResult<Awaited<ReturnType<typeof confirmPayment>>, TError, {
    paymentId: number;
}, TContext>;
export {};
//# sourceMappingURL=api.d.ts.map