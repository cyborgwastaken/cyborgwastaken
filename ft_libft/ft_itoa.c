/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_itoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/10/30 13:40:35 by gcyril            #+#    #+#             */
/*   Updated: 2019/11/06 15:32:08 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"
#include <stdio.h>

static int	itoalen(int n)
{
	int	res;

	res = (n <= 0 ? 1 : 0);
	while (n != 0)
	{
		n = n / 10;
		res++;
	}
	return (res);
}

char		*ft_itoa(int n)
{
	unsigned int		num;
	char				*itoa;
	int					size;

	num = (n < 0 ? -n : n);
	size = itoalen(n);
	if (!(itoa = (char *)malloc(sizeof(char) * (size + 1))))
		return (NULL);
	itoa[size--] = '\0';
	while (size >= 0)
	{
		itoa[size] = num % 10 + 48;
		num = num / 10;
		size--;
	}
	if (n < 0)
		itoa[0] = '-';
	return (itoa);
}
